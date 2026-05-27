"""Result dataclasses for application services."""

from __future__ import annotations

from dataclasses import dataclass

from memory_distiller.domain.candidate import MemoryCandidate, ValidatedCandidate
from memory_distiller.domain.memory_entry import MemoryDocument


@dataclass(frozen=True)
class ExtractionPromptResult:
    """Result of rendering an extraction prompt."""

    prompt: str


@dataclass(frozen=True)
class ExtractionRunResult:
    """Result of running the extraction service."""

    prompt: str
    raw_response: str
    candidates: list[MemoryCandidate]


@dataclass(frozen=True)
class ValidationPromptResult:
    """Result of rendering a validation prompt."""

    prompt: str


@dataclass(frozen=True)
class ValidationRunResult:
    """Result of running the validation service."""

    prompt: str
    raw_response: str
    validated_candidates: list[ValidatedCandidate]


@dataclass(frozen=True)
class MergePromptResult:
    """Result of rendering a merge prompt."""

    prompt: str


@dataclass(frozen=True)
class MergeRunResult:
    """Result of running the merge service."""

    prompt: str
    raw_response: str
    memory_document: MemoryDocument


@dataclass(frozen=True)
class CompressionPromptResult:
    """Result of rendering a compression prompt."""

    prompt: str


@dataclass(frozen=True)
class CompressionRunResult:
    """Result of running the compression service."""

    prompt: str
    raw_response: str
    memory_prompt: str


@dataclass(frozen=True)
class PipelinePromptBundle:
    """Bundle of all prompts for the pipeline."""

    extractor_prompt: str
    validator_prompt: str | None
    merger_prompt: str | None
    compressor_prompt: str | None
