"""Merge service for merging validated candidates into a memory document."""

from __future__ import annotations

from memory_distiller.application.models import MergeRunResult
from memory_distiller.io.memory_parser import parse_memory_document
from memory_distiller.llm.base import LlmClient
from memory_distiller.prompts.render import render_merger_prompt


class MergeService:
    """Service for merging validated candidates into a memory document."""

    def render_prompt(self, *, existing_memory: str, validated_candidates: str) -> str:
        """Render merger prompt.

        Args:
            existing_memory: Existing memory content.
            validated_candidates: Validated candidates string.

        Returns:
            Rendered prompt string.

        Raises:
            ValueError: If validated_candidates is missing or None.
        """
        return render_merger_prompt(existing_memory, validated_candidates)

    def run(
        self,
        *,
        existing_memory: str,
        validated_candidates: str,
        llm_client: LlmClient,
        system_prompt: str = "Du bist ein Memory-Merger.",
    ) -> MergeRunResult:
        """Run merge: render prompt, call LLM, parse memory document.

        Args:
            existing_memory: Existing memory content.
            validated_candidates: Validated candidates string.
            llm_client: LLM client to use for completion.
            system_prompt: System prompt for the LLM.

        Returns:
            MergeRunResult with prompt, raw_response, and memory_document.

        Raises:
            ValueError: If validated_candidates is missing or None.
            ParseErrorCollection: If LLM response cannot be parsed.
        """
        prompt = render_merger_prompt(existing_memory, validated_candidates)
        raw_response = llm_client.complete(system_prompt=system_prompt, user_prompt=prompt)
        memory_document = parse_memory_document(raw_response)
        return MergeRunResult(
            prompt=prompt, raw_response=raw_response, memory_document=memory_document
        )
