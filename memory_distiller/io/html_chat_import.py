"""HTML chat export parsing utilities."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import Final

# Message class patterns to detect chat messages
_MESSAGE_CLASS_PATTERNS: Final[list[str]] = [
    r"\bmessage\b",
    r"\buser-message\b",
    r"\bassistant-message\b",
]

# Tags whose content should be replaced with placeholder
_IMAGE_TAGS: Final[set[str]] = {"img", "image", "figcaption"}
_PLACEHOLDER_TAGS: Final[set[str]] = {"figure"}

# Tags to completely ignore
_IGNORE_TAGS: Final[set[str]] = {"script", "style", "nav", "header", "footer", "aside"}

# Block-level tags that need separation between their content
_BLOCK_TAGS: Final[set[str]] = {
    "p",
    "li",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
    "td",
    "th",
    "div",
    "section",
    "article",
}

# Separator to insert at start of block tags
_BLOCK_START_SEPARATORS: Final[dict[str, str]] = {
    "p": "\n\n",
    "li": "\n- ",
    "pre": "\n",
    "h1": "\n\n",
    "h2": "\n\n",
    "h3": "\n\n",
    "h4": "\n\n",
    "h5": "\n\n",
    "h6": "\n\n",
    "blockquote": "\n\n",
    "td": " | ",
    "th": " | ",
}

# Separator to insert at end of block tags
_BLOCK_END_SEPARATORS: Final[dict[str, str]] = {
    "p": "\n\n",
    "li": "",
    "pre": "\n",
    "h1": "\n\n",
    "h2": "\n\n",
    "h3": "\n\n",
    "h4": "\n\n",
    "h5": "\n\n",
    "h6": "\n\n",
    "blockquote": "\n\n",
    "td": "",
    "th": "",
}


class HtmlChatImportError(Exception):
    """Raised when HTML chat import parsing fails."""

    pass


class _ChatMessage:
    """Represents a single chat message."""

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def __repr__(self) -> str:
        return f"_ChatMessage(role={self.role!r}, content={self.content[:20]!r}...)"


class _ChatHtmlParser(HTMLParser):
    """HTML parser that extracts chat messages from ChatGPT HTML exports."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[_ChatMessage] = []
        self._current_role: str | None = None
        self._current_content: list[str] = []
        self._tag_stack: list[str] = []
        self._ignore_depth: int = 0
        self._in_message: bool = False
        self._found_any_message: bool = False
        self._message_tag: str | None = None
        self._message_depth: int = 0
        self._last_was_block_end: bool = False
        self._pending_separator: str = ""

    def _is_message_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        """Check if tag is a message container based on class attribute."""
        class_attr = ""
        for name, value in attrs:
            if name == "class" and value is not None:
                class_attr = value.lower()
                break
        if not class_attr:
            return False
        for pattern in _MESSAGE_CLASS_PATTERNS:
            if re.search(pattern, class_attr):
                return True
        return False

    def _is_user_message(self, attrs: list[tuple[str, str | None]]) -> bool:
        """Check if message is from user based on class or other indicators."""
        class_attr = ""
        for name, value in attrs:
            if name == "class" and value is not None:
                class_attr = value.lower()
                break
        if not class_attr:
            return False
        return bool(re.search(r"\buser\b", class_attr))

    def _is_assistant_message(self, attrs: list[tuple[str, str | None]]) -> bool:
        """Check if message is from assistant based on class or other indicators."""
        class_attr = ""
        for name, value in attrs:
            if name == "class" and value is not None:
                class_attr = value.lower()
                break
        if not class_attr:
            return False
        return bool(re.search(r"\b(assistant|bot|ai)\b", class_attr))

    def _start_message(self, role: str, tag: str) -> None:
        """Start collecting content for a new message."""
        self._current_role = role
        self._current_content = []
        self._in_message = True
        self._found_any_message = True
        self._message_tag = tag
        self._message_depth = 1

    def _finish_message(self) -> None:
        """Finish current message and store it."""
        if self._current_role and self._current_content:
            content = "".join(self._current_content).strip()
            # Normalize whitespace: collapse 3+ newlines to 2, collapse spaces/tabs
            content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)
            content = re.sub(r"[ \t]+", " ", content)
            # Strip each line and remove blank lines at start/end
            content = "\n".join(line.strip() for line in content.splitlines())
            content = content.strip()
            if content:
                self.messages.append(_ChatMessage(self._current_role, content))
        self._current_role = None
        self._current_content = []
        self._in_message = False
        self._message_tag = None
        self._message_depth = 0
        self._last_was_block_end = False
        self._pending_separator = ""

    def _handle_img_tag(self, attrs: list[tuple[str, str | None]]) -> None:
        """Handle img tag by adding placeholder."""
        if self._in_message:
            alt_text = ""
            for name, value in attrs:
                if name == "alt" and value:
                    alt_text = value
                    break
            if alt_text:
                self._current_content.append(f"[image: {alt_text}]")
            else:
                self._current_content.append("[image]")

    def _handle_placeholder_tag(self, tag: str) -> None:
        """Handle tags that should be replaced with placeholder."""
        if self._in_message:
            self._current_content.append(f"[{tag}]")

    def _handle_break_tag(self) -> None:
        """Handle <br> tags."""
        if self._in_message:
            self._current_content.append("\n")

    def _append_content(self, text: str) -> None:
        """Append text content, applying any pending separator first."""
        if not text:
            return
        if self._pending_separator:
            sep = self._pending_separator
            self._pending_separator = ""
            self._current_content.append(sep)
        self._current_content.append(text)
        self._last_was_block_end = False

    def _append_separator(self, sep: str) -> None:
        """Mark a pending block separator to prepend to next content."""
        if not sep:
            return
        if self._current_content:
            # Content already present - add separator directly
            self._current_content.append(sep)
            self._last_was_block_end = True
        else:
            # No content yet - store as pending separator
            self._pending_separator = sep

    # pylint: disable=invalid-name
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle opening tags."""
        tag_lower = tag.lower()

        if tag_lower in _IGNORE_TAGS:
            self._ignore_depth += 1
            return

        if self._ignore_depth > 0:
            return

        if tag_lower in ("br", "hr"):
            self._handle_break_tag()
            return

        if tag_lower in _PLACEHOLDER_TAGS:
            self._handle_placeholder_tag(tag_lower)
            return

        if tag_lower == "img":
            self._handle_img_tag(attrs)
            return

        # Check if this is a message container
        if self._is_message_tag(tag_lower, attrs):
            if self._in_message:
                if tag_lower == self._message_tag:
                    # Nested same message tag - increase depth
                    self._message_depth += 1
                    self._tag_stack.append(tag_lower)
                    return
                else:
                    # Different message tag - finish current, start new
                    self._finish_message()
                    role = "user" if self._is_user_message(attrs) else "assistant"
                    self._start_message(role, tag_lower)
                    self._tag_stack.append(tag_lower)
                    return
            else:
                role = "user" if self._is_user_message(attrs) else "assistant"
                self._start_message(role, tag_lower)
                self._tag_stack.append(tag_lower)
                return

        # Track tags inside messages for content extraction
        if self._in_message:
            self._tag_stack.append(tag_lower)
            # Add block separator at start of block tags
            if tag_lower in _BLOCK_START_SEPARATORS:
                self._append_separator(_BLOCK_START_SEPARATORS[tag_lower])

    # pylint: disable=invalid-name
    def handle_endtag(self, tag: str) -> None:
        """Handle closing tags."""
        tag_lower = tag.lower()

        if tag_lower in _IGNORE_TAGS:
            self._ignore_depth = max(0, self._ignore_depth - 1)
            return

        if self._ignore_depth > 0:
            return

        if self._in_message and tag_lower == self._message_tag:
            # Closing the message tag we're tracking
            self._message_depth -= 1
            if self._message_depth == 0:
                self._finish_message()
            elif self._tag_stack and self._tag_stack[-1] == tag_lower:
                self._tag_stack.pop()
            return

        if self._in_message:
            # Add block separator at end of block tags before popping
            if tag_lower in _BLOCK_END_SEPARATORS:
                self._append_separator(_BLOCK_END_SEPARATORS[tag_lower])
            if self._tag_stack:
                self._tag_stack.pop()

    # pylint: disable=invalid-name
    def handle_data(self, data: str) -> None:
        """Handle text data."""
        if self._ignore_depth > 0:
            return

        if self._in_message:
            self._append_content(data)

    # pylint: disable=invalid-name
    def handle_entityref(self, name: str) -> None:
        """Handle named HTML entities."""
        if self._ignore_depth > 0:
            return
        if self._in_message:
            self._append_content(html.unescape(f"&{name};"))

    # pylint: disable=invalid-name
    def handle_charref(self, name: str) -> None:
        """Handle numeric HTML character references."""
        if self._ignore_depth > 0:
            return
        if self._in_message:
            self._append_content(html.unescape(f"&#{name};"))

    def error(self, message: str) -> None:
        """Override to suppress HTMLParseError warnings in Python 3.12+."""
        pass


def parse_chatgpt_html_export(html_content: str) -> str:
    """Parse ChatGPT HTML export and convert to plain text format.

    Args:
        html_content: HTML string from ChatGPT export.

    Returns:
        Plain text string in format "User: <text>\\n\\nAssistant: <text>" etc.

    Raises:
        HtmlChatImportError: If no supported message structure is found
            or parsing fails.
    """
    if not html_content or not html_content.strip():
        raise HtmlChatImportError("Empty HTML content provided")

    parser = _ChatHtmlParser()
    try:
        parser.feed(html_content)
    except Exception as e:
        raise HtmlChatImportError(f"Failed to parse HTML: {e}") from e

    # Finish any pending message
    if parser._in_message:  # pylint: disable=protected-access
        parser._finish_message()  # pylint: disable=protected-access

    if not parser.messages and not parser._found_any_message:  # pylint: disable=protected-access
        raise HtmlChatImportError(
            "No supported message structure found in HTML. "
            "Expected classes like .message, .user-message, or .assistant-message."
        )

    # Build output string
    lines: list[str] = []
    for msg in parser.messages:
        role_label = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role_label}: {msg.content}")

    result = "\n\n".join(lines)

    # Decode any remaining HTML entities
    result = html.unescape(result)

    return result
