"""Tests for html_chat_import module."""

from __future__ import annotations

import pytest

from memory_distiller.io.html_chat_import import (
    HtmlChatImportError,
    parse_chatgpt_html_export,
)


class TestMinimalExampleConversion:
    """Test minimal example conversion (exact structure from issue)."""

    def test_minimal_user_assistant_html(self) -> None:
        """Minimal HTML with user and assistant messages (Issue #29 structure)."""
        html = (
            '<div class="conversation">'
            '<div class="message user-message"><div class="content">'
            "<p>Hallo, das hier soll ein Beispiel werden</p></div></div>"
            '<div class="message assistant-message"><div class="content">'
            "<p>Hallo! Klingt gut — wofür soll es ein Beispiel werden?</p>"
            "</div></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "User: Hallo, das hier soll ein Beispiel werden" in result
        assert "Assistant: Hallo! Klingt gut — wofür soll es ein Beispiel werden?" in result


class TestOrderPreservation:
    """Test message order preservation."""

    def test_user_assistant_user_assistant_order(self) -> None:
        """Messages should appear in document order with nested content."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>First user message</p></div></div>"
            '<div class="message assistant-message"><div class="content">'
            "<p>First assistant</p></div></div>"
            '<div class="message user-message"><div class="content">'
            "<p>Second user message</p></div></div>"
            '<div class="message assistant-message"><div class="content">'
            "<p>Second assistant</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        lines = result.split("\n\n")
        assert len(lines) == 4
        assert "User: First user message" in lines[0]
        assert "Assistant: First assistant" in lines[1]
        assert "User: Second user message" in lines[2]
        assert "Assistant: Second assistant" in lines[3]


class TestUnicodePreservation:
    """Test Unicode character preservation."""

    def test_german_umlauts_preserved(self) -> None:
        """German umlauts should be preserved."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>Grüße aus Österreich</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "Grüße aus Österreich" in result

    def test_em_dash_preserved(self) -> None:
        """Em dash should be preserved."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>Das ist — glaube ich — richtig</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "—" in result

    def test_german_punctuation_preserved(self) -> None:
        """German punctuation style should be preserved."""
        html = (
            '<div class="message assistant-message"><div class="content">'
            "<p>Das ist korrekt, oder?</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "Das ist korrekt, oder?" in result


class TestIgnoreScriptStyle:
    """Test that script and style content is ignored."""

    def test_script_content_ignored(self) -> None:
        """Script tag content should not appear in output."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>Real message</p></div></div>"
            '<script>document.cookie = "evil";</script>'
            '<div class="message assistant-message"><div class="content">'
            "<p>Another real message</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "Real message" in result
        assert "Another real message" in result
        assert "cookie" not in result
        assert "evil" not in result

    def test_style_content_ignored(self) -> None:
        """Style tag content should not appear in output."""
        html = (
            "<style>.message { color: red; }</style>"
            '<div class="message user-message"><div class="content">'
            "<p>Styled but visible</p></div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "Styled but visible" in result
        assert "color: red" not in result


class TestUnknownHtmlRaisesError:
    """Test that unknown HTML structure raises HtmlChatImportError."""

    def test_empty_html_raises_error(self) -> None:
        """Empty HTML should raise HtmlChatImportError."""
        with pytest.raises(HtmlChatImportError, match="Empty HTML content"):
            parse_chatgpt_html_export("")

    def test_whitespace_only_html_raises_error(self) -> None:
        """Whitespace-only HTML should raise HtmlChatImportError."""
        with pytest.raises(HtmlChatImportError, match="Empty HTML content"):
            parse_chatgpt_html_export("   \n\t  ")

    def test_no_message_structure_raises_error(self) -> None:
        """HTML without message structure should raise HtmlChatImportError."""
        html = "<html><body><p>Just a paragraph</p></body></html>"
        with pytest.raises(HtmlChatImportError, match="No supported message structure"):
            parse_chatgpt_html_export(html)

    def test_unrelated_divs_raze_error(self) -> None:
        """Divs without message classes should raise HtmlChatImportError."""
        html = "<div><p>Some text</p></div><div><span>More text</span></div>"
        with pytest.raises(HtmlChatImportError, match="No supported message structure"):
            parse_chatgpt_html_export(html)


class TestListsCodeReadable:
    """Test that lists and code are readable."""

    def test_list_items_readable(self) -> None:
        """List items should have their text extracted."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<ul><li>First item</li><li>Second item</li><li>Third item</li></ul>"
            "</div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "First item" in result
        assert "Second item" in result
        assert "Third item" in result

    def test_code_blocks_readable(self) -> None:
        """Code blocks should have their text extracted."""
        html = (
            '<div class="message assistant-message"><div class="content">'
            '<pre><code>def hello():\n    print("world")</code></pre>'
            "</div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "def hello():" in result
        assert 'print("world")' in result

    def test_paragraphs_readable(self) -> None:
        """Paragraphs should have their text extracted."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>First paragraph</p><p>Second paragraph</p>"
            "</div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "First paragraph" in result
        assert "Second paragraph" in result


class TestImagePlaceholder:
    """Test image handling with placeholders."""

    def test_img_replaced_with_placeholder(self) -> None:
        """Images should be replaced with placeholder."""
        html = (
            '<div class="message user-message"><div class="content">'
            "<p>Look at this:</p>"
            '<img src="picture.png" alt="A nice sunset" />'
            "</div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "Look at this:" in result
        assert "[image: A nice sunset]" in result

    def test_img_without_alt_replaced(self) -> None:
        """Images without alt text get generic placeholder."""
        html = (
            '<div class="message user-message"><div class="content">'
            '<img src="graph.png" />'
            "</div></div>"
        )
        result = parse_chatgpt_html_export(html)
        assert "[image]" in result
