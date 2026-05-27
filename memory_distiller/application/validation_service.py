"""Validation service for validating memory candidates."""

from __future__ import annotations

from memory_distiller.application.models import ValidationRunResult
from memory_distiller.io.candidate_parser import parse_validated_candidates
from memory_distiller.llm.base import LlmClient
from memory_distiller.prompts.render import render_validator_prompt


class ValidationService:
    """Service for validating memory candidates."""

    def render_prompt(self, *, existing_memory: str, chat_log: str, candidates: str) -> str:
        """Render validator prompt.

        Args:
            existing_memory: Existing memory content.
            chat_log: Chat log content.
            candidates: Candidates string to validate.

        Returns:
            Rendered prompt string.

        Raises:
            ValueError: If chat_log or candidates is missing or None.
        """
        return render_validator_prompt(existing_memory, chat_log, candidates)

    def run(
        self,
        *,
        existing_memory: str,
        chat_log: str,
        candidates: str,
        llm_client: LlmClient,
        system_prompt: str = "Du bist ein strenger Memory-Validator.",
    ) -> ValidationRunResult:
        """Run validation: render prompt, call LLM, parse validated candidates.

        Args:
            existing_memory: Existing memory content.
            chat_log: Chat log content.
            candidates: Candidates string to validate.
            llm_client: LLM client to use for completion.
            system_prompt: System prompt for the LLM.

        Returns:
            ValidationRunResult with prompt, raw_response, and validated_candidates.

        Raises:
            ValueError: If chat_log or candidates is missing or None.
            ParseErrorCollection: If LLM response cannot be parsed.
        """
        prompt = render_validator_prompt(existing_memory, chat_log, candidates)
        raw_response = llm_client.complete(system_prompt=system_prompt, user_prompt=prompt)
        validated_candidates = parse_validated_candidates(raw_response)
        return ValidationRunResult(
            prompt=prompt, raw_response=raw_response, validated_candidates=validated_candidates
        )
