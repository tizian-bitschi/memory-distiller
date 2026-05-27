"""Pipeline service for orchestrating the memory distiller pipeline."""

from __future__ import annotations

from memory_distiller.application.compression_service import CompressionService
from memory_distiller.application.extraction_service import ExtractionService
from memory_distiller.application.merge_service import MergeService
from memory_distiller.application.models import PipelinePromptBundle
from memory_distiller.application.validation_service import ValidationService


class PipelineService:
    """Service for orchestrating the memory distiller pipeline."""

    def __init__(
        self,
        extraction_service: ExtractionService | None = None,
        validation_service: ValidationService | None = None,
        merge_service: MergeService | None = None,
        compression_service: CompressionService | None = None,
    ) -> None:
        """Initialize pipeline service with optional service dependencies.

        Args:
            extraction_service: Service for extracting candidates. Defaults to ExtractionService().
            validation_service: Service for validating candidates. Defaults to ValidationService().
            merge_service: Service for merging candidates. Defaults to MergeService().
            compression_service: Service for compressing memory. Defaults to CompressionService().
        """
        self.extraction_service = extraction_service or ExtractionService()
        self.validation_service = validation_service or ValidationService()
        self.merge_service = merge_service or MergeService()
        self.compression_service = compression_service or CompressionService()

    def render_all_prompts(
        self,
        *,
        existing_memory: str,
        chat_log: str,
        candidates: str = "",
        validated_candidates: str = "",
        memory_full: str = "",
        next_context: str = "",
    ) -> PipelinePromptBundle:
        """Render all pipeline prompts based on provided inputs.

        Args:
            existing_memory: Existing memory content.
            chat_log: Chat log content.
            candidates: Candidates string (required for validator prompt).
            validated_candidates: Validated candidates string (required for merger prompt).
            memory_full: Full memory content (required for compressor prompt).
            next_context: Optional next context hint for compressor.

        Returns:
            PipelinePromptBundle containing all rendered prompts.
                validator_prompt is None if candidates is empty.
                merger_prompt is None if validated_candidates is empty.
                compressor_prompt is None if memory_full is empty.
        """
        # Always render extractor prompt
        extractor_prompt_str = self.extraction_service.render_prompt(
            existing_memory=existing_memory, chat_log=chat_log
        )

        # Validator prompt only if candidates provided
        validator_prompt_str = None
        if candidates:
            validator_prompt_str = self.validation_service.render_prompt(
                existing_memory=existing_memory, chat_log=chat_log, candidates=candidates
            )

        # Merger prompt only if validated_candidates provided
        merger_prompt_str = None
        if validated_candidates:
            merger_prompt_str = self.merge_service.render_prompt(
                existing_memory=existing_memory, validated_candidates=validated_candidates
            )

        # Compressor prompt only if memory_full provided
        compressor_prompt_str = None
        if memory_full:
            compressor_prompt_str = self.compression_service.render_prompt(
                memory_full=memory_full, next_context=next_context
            )

        return PipelinePromptBundle(
            extractor_prompt=extractor_prompt_str,
            validator_prompt=validator_prompt_str,
            merger_prompt=merger_prompt_str,
            compressor_prompt=compressor_prompt_str,
        )
