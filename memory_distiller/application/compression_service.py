"""Compression service for compressing memory into a prompt-friendly format."""

from __future__ import annotations

from memory_distiller.application.models import CompressionRunResult
from memory_distiller.llm.base import LlmClient
from memory_distiller.prompts.render import render_compressor_prompt


class CompressionService:
    """Service for compressing memory into a prompt-friendly format."""

    def render_prompt(self, *, memory_full: str, next_context: str = "") -> str:
        """Render compressor prompt.

        Args:
            memory_full: Full memory content.
            next_context: Optional next context hint.

        Returns:
            Rendered prompt string.

        Raises:
            ValueError: If memory_full is missing or None.
        """
        return render_compressor_prompt(memory_full, next_context)

    def run(
        self,
        *,
        memory_full: str,
        next_context: str = "",
        llm_client: LlmClient,
        system_prompt: str = "Du bist ein Memory-Kompressor für LLM-Prompts.",
    ) -> CompressionRunResult:
        """Run compression: render prompt, call LLM, return raw response as memory_prompt.

        Args:
            memory_full: Full memory content.
            next_context: Optional next context hint.
            llm_client: LLM client to use for completion.
            system_prompt: System prompt for the LLM.

        Returns:
            CompressionRunResult with prompt, raw_response, and memory_prompt.

        Raises:
            ValueError: If memory_full is missing or None.
        """
        prompt = render_compressor_prompt(memory_full, next_context)
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
        return CompressionRunResult(
            prompt=prompt,
            raw_response=raw_response,
            memory_prompt=raw_response,
            usage=usage,
            cost_estimate=cost_estimate,
            model=model,
        )
