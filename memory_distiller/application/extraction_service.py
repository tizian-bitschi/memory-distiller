"""Extraction service for extracting memory candidates from chat logs."""

from __future__ import annotations

from memory_distiller.application.models import ExtractionRunResult
from memory_distiller.io.candidate_parser import parse_candidates
from memory_distiller.llm.base import LlmClient
from memory_distiller.prompts.render import render_extractor_prompt


class ExtractionService:
    """Service for extracting memory candidates from chat logs."""

    def render_prompt(self, *, existing_memory: str, chat_log: str) -> str:
        """Render extractor prompt.

        Args:
            existing_memory: Existing memory content.
            chat_log: Chat log content to extract from.

        Returns:
            Rendered prompt string.

        Raises:
            ValueError: If chat_log is missing or None.
        """
        return render_extractor_prompt(existing_memory, chat_log)

    def run(
        self,
        *,
        existing_memory: str,
        chat_log: str,
        llm_client: LlmClient,
        system_prompt: str = "Du bist ein strenger Memory-Extractor.",
    ) -> ExtractionRunResult:
        """Run extraction: render prompt, call LLM, parse candidates.

        Args:
            existing_memory: Existing memory content.
            chat_log: Chat log content to extract from.
            llm_client: LLM client to use for completion.
            system_prompt: System prompt for the LLM.

        Returns:
            ExtractionRunResult with prompt, raw_response, and candidates.

        Raises:
            ValueError: If chat_log is missing or None.
            ParseErrorCollection: If LLM response cannot be parsed.
        """
        prompt = render_extractor_prompt(existing_memory, chat_log)
        if hasattr(llm_client, "complete_with_usage"):
            llm_response = llm_client.complete_with_usage(
                system_prompt=system_prompt, user_prompt=prompt
            )
            raw_response = llm_response.content
            usage = llm_response.usage
            cost_estimate = llm_response.cost_estimate
            model = llm_response.model
        else:
            raw_response = llm_client.complete(system_prompt=system_prompt, user_prompt=prompt)
            usage = None
            cost_estimate = None
            model = None
        candidates = parse_candidates(raw_response)
        return ExtractionRunResult(
            prompt=prompt,
            raw_response=raw_response,
            candidates=candidates,
            usage=usage,
            cost_estimate=cost_estimate,
            model=model,
        )
