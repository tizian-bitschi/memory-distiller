"""Tests for prompt rendering functions."""

import re

import pytest

from memory_distiller.prompts import (
    render_compressor_prompt,
    render_extractor_prompt,
    render_merger_prompt,
    render_validator_prompt,
)


class TestRenderExtractorPrompt:
    """Tests for render_extractor_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_extractor_prompt("", "chat")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        chat = "chat content"
        result = render_extractor_prompt(existing, chat)
        assert existing in result

    def test_contains_chat_log(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory"
        chat = "chat content here"
        result = render_extractor_prompt(existing, chat)
        assert chat in result

    def test_contains_candidate_output_format(self) -> None:
        """Extractor prompt contains exact candidate output format."""
        result = render_extractor_prompt("", "chat")
        assert "ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_extractor_prompt("existing", "chat")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_extractor_prompt("", "chat")
        assert isinstance(result, str)
        assert "chat" in result

    def test_missing_chat_log_raises_value_error(self) -> None:
        """Missing chat_log raises ValueError."""
        with pytest.raises(ValueError, match="chat_log is required"):
            render_extractor_prompt("existing", None)  # type: ignore

    def test_contains_english_instruction_text(self) -> None:
        """Extractor prompt contains English instruction text."""
        result = render_extractor_prompt("", "chat")
        assert "You are a memory extractor" in result

    def test_contains_invalid_alias_warning(self) -> None:
        """Extractor prompt warns against invalid aliases."""
        result = render_extractor_prompt("", "chat")
        assert "INVALID-ALIAS WARNING" in result
        assert "PREFERENCE" in result
        assert "GLOBAL" in result

    def test_contains_canonical_example_with_project_scope(self) -> None:
        """Extractor prompt contains valid canonical example with P:RecipeBot."""
        result = render_extractor_prompt("", "chat")
        assert "P:RecipeBot" in result

    def test_contains_canonical_example_with_priority_and_stability(self) -> None:
        """Extractor prompt contains valid canonical example with H and D."""
        result = render_extractor_prompt("", "chat")
        assert "|H|D|" in result

    def test_canonical_example_does_not_use_invalid_aliases(self) -> None:
        """Canonical example does not use invalid aliases like PREFERENCE or GLOBAL."""
        result = render_extractor_prompt("", "chat")
        # Extract the portion after "Canonical Example"
        if "Canonical Example" in result:
            example_start = result.find("Canonical Example")
            example_section = result[example_start:]
            # The example should be before "Do not output any explanation"
            if "Do not output any explanation" in example_section:
                example_section = example_section[
                    : example_section.find("Do not output any explanation")
                ]
            # Check that invalid aliases are not in the example section
            assert "PREFERENCE" not in example_section, "Example should use PREF, not PREFERENCE"
            assert "GLOBAL" not in example_section, "Example should use G, not GLOBAL"
            assert "STABLE" not in example_section, "Example should use D, not STABLE"


class TestRenderValidatorPrompt:
    """Tests for render_validator_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_validator_prompt("", "chat", "candidates")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        result = render_validator_prompt(existing, "chat", "candidates")
        assert existing in result

    def test_contains_chat_log(self) -> None:
        """Each prompt contains its inserted input."""
        chat = "chat content here"
        result = render_validator_prompt("", chat, "candidates")
        assert chat in result

    def test_contains_candidates(self) -> None:
        """Each prompt contains its inserted input."""
        candidates = "candidate content here"
        result = render_validator_prompt("", "chat", candidates)
        assert candidates in result

    def test_contains_validated_candidate_output_format(self) -> None:
        """Validator prompt contains exact validated candidate output format."""
        result = render_validator_prompt("", "chat", "candidates")
        assert (
            "ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON" in result
        )

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_validator_prompt("existing", "chat", "candidates")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_validator_prompt("", "chat", "candidates")
        assert isinstance(result, str)

    def test_missing_chat_log_raises_value_error(self) -> None:
        """Missing chat_log raises ValueError."""
        with pytest.raises(ValueError, match="chat_log is required"):
            render_validator_prompt("existing", None, "candidates")  # type: ignore

    def test_missing_candidates_raises_value_error(self) -> None:
        """Missing candidates for validator raises ValueError."""
        with pytest.raises(ValueError, match="candidates is required"):
            render_validator_prompt("existing", "chat", None)  # type: ignore

    def test_contains_english_instruction_text(self) -> None:
        """Validator prompt contains English instruction text."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "You are a strict memory validator" in result

    def test_contains_invalid_alias_warning(self) -> None:
        """Validator prompt warns against invalid aliases."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "INVALID-ALIAS WARNING" in result
        assert "PREFERENCE" in result
        assert "GLOBAL" in result

    def test_contains_canonical_example_with_pref(self) -> None:
        """Validator prompt contains valid canonical example with PREF."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "PREF" in result

    def test_canonical_example_does_not_use_invalid_aliases(self) -> None:
        """Canonical example does not use invalid aliases like PREFERENCE or GLOBAL."""
        result = render_validator_prompt("", "chat", "candidates")
        if "Canonical Example" in result:
            example_start = result.find("Canonical Example")
            example_section = result[example_start:]
            if "Rules:" in example_section:
                example_section = example_section[: example_section.find("Rules:")]
            assert "PREFERENCE" not in example_section, "Example should use PREF, not PREFERENCE"
            assert "GLOBAL" not in example_section, "Example should use G, not GLOBAL"
            assert "STABLE" not in example_section, "Example should use D, not STABLE"

    def test_contains_pref_vs_rule_guidance(self) -> None:
        """Validator prompt explains PREF vs RULE type usage."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "Use TYPE = PREF" in result
        assert "Use TYPE = RULE" in result
        assert "preferences, defaults" in result
        assert "hard constraints" in result

    def test_contains_canonical_pref_example_for_metric_units(self) -> None:
        """Validator prompt contains PREF example for metric units."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "P:RecipeBot|PREF|H|D" in result
        assert "metric units" in result

    def test_contains_verdict_as_second_column_guidance(self) -> None:
        """Validator prompt contains guidance about VERDICT as second column."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "VERDICT as the second column" in result

    def test_contains_do_not_output_extractor_candidate_format(self) -> None:
        """Validator prompt warns against extractor candidate format."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "Do NOT output extractor candidate format" in result

    def test_contains_invalid_example_fragment(self) -> None:
        """Validator prompt contains invalid example fragment."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "M1|ADD|-|P:RecipeBot|RULE|H|D" in result

    def test_contains_valid_example_fragment(self) -> None:
        """Validator prompt contains valid example fragment."""
        result = render_validator_prompt("", "chat", "candidates")
        assert "M1|KEEP|ADD|-|P:RecipeBot|RULE|H|D" in result

    # Part A – Temporary-detail boundary guidance
    def test_contains_temporary_boundary_do_not_remember_this(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "do not remember this" in result.lower()

    def test_contains_temporary_boundary_nearest_detail(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "nearest or explicitly referenced temporary detail" in result

    def test_contains_temporary_boundary_no_retroactive_drop(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "Do not retroactively drop earlier explicit reusable project instructions" in result

    def test_contains_temporary_boundary_keep_recipebot_style(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "KEEP the RecipeBot style instruction" in result

    def test_contains_temporary_boundary_drop_pipeline_test(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "DROP the temporary pipeline-test fact" in result

    # Part B – Contradictory verdict/action guidance
    def test_contains_contradictory_do_not_emit_keep_ignore(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "Do not emit KEEP|IGNORE" in result

    def test_contains_contradictory_do_not_emit_edit_ignore(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "Do not emit EDIT|IGNORE" in result

    def test_contains_contradictory_action_ignore_use_drop(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "For ACTION=IGNORE, use VERDICT=DROP" in result

    def test_contains_contradictory_invalid_keep_ignore_example(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "M8|KEEP|IGNORE" in result

    def test_contains_contradictory_valid_drop_ignore_example(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "M8|DROP|IGNORE" in result

    # Part C – Existing-memory update guidance
    def test_contains_existing_memory_refines_concretizes(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "refines or concretizes an existing memory entry" in result

    def test_contains_existing_memory_prefer_edit_update(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "prefer EDIT|UPDATE" in result

    def test_contains_existing_memory_markdown_files_repo(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "Markdown files in the repository" in result

    def test_contains_existing_memory_avoid_database_now(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        assert "avoid a database for now" in result

    def test_contains_existing_memory_update_example(self) -> None:
        result = render_validator_prompt("", "chat", "candidates")
        expected = (
            "M6|EDIT|UPDATE|RecipeBot should prefer simple file-based storage "
            "over database complexity.|P:RecipeBot|DECISION|H|M"
        )
        assert expected in result


class TestRenderMergerPrompt:
    """Tests for render_merger_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_merger_prompt("", "validated")
        assert isinstance(result, str)

    def test_contains_existing_memory(self) -> None:
        """Each prompt contains its inserted input."""
        existing = "existing memory content"
        result = render_merger_prompt(existing, "validated candidates")
        assert existing in result

    def test_contains_validated_candidates(self) -> None:
        """Each prompt contains its inserted input."""
        validated = "validated candidates content"
        result = render_merger_prompt("", validated)
        assert validated in result

    def test_contains_memory_full(self) -> None:
        """Merger prompt contains # MEMORY_FULL."""
        result = render_merger_prompt("", "validated")
        assert "# MEMORY_FULL" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_merger_prompt("existing", "validated")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_existing_memory_allowed(self) -> None:
        """Test empty existing_memory is allowed."""
        result = render_merger_prompt("", "validated")
        assert isinstance(result, str)
        assert "validated" in result

    def test_missing_validated_candidates_raises_value_error(self) -> None:
        """Missing validated_candidates raises ValueError."""
        with pytest.raises(ValueError, match="validated_candidates is required"):
            render_merger_prompt("existing", None)  # type: ignore

    def test_contains_english_instruction_text(self) -> None:
        """Merger prompt contains English instruction text."""
        result = render_merger_prompt("", "validated")
        assert "You are a memory merger" in result

    def test_contains_invalid_alias_warning(self) -> None:
        """Merger prompt warns against invalid aliases."""
        result = render_merger_prompt("", "validated")
        assert "INVALID-ALIAS WARNING" in result
        assert "Do NOT use these as SCOPE field values" in result
        assert "PREFERENCE" in result
        assert "GLOBAL" in result

    def test_contains_section_header_note(self) -> None:
        """Merger prompt notes that section headers like ## GLOBAL are allowed."""
        result = render_merger_prompt("", "validated")
        assert "Section headers such as ## GLOBAL" in result

    def test_contains_memory_full_header(self) -> None:
        """Merger prompt contains # MEMORY_FULL header."""
        result = render_merger_prompt("", "validated")
        assert "# MEMORY_FULL" in result

    def test_contains_global_section_header(self) -> None:
        """Merger prompt contains ## GLOBAL section header."""
        result = render_merger_prompt("", "validated")
        assert "## GLOBAL" in result

    def test_contains_projects_section_header(self) -> None:
        """Merger prompt contains ## PROJECTS section header."""
        result = render_merger_prompt("", "validated")
        assert "## PROJECTS" in result

    def test_contains_canonical_example_with_g_rule(self) -> None:
        """Merger prompt contains valid canonical example with G|RULE|H|D."""
        result = render_merger_prompt("", "validated")
        assert "G|RULE|H|D" in result

    def test_contains_canonical_example_with_project_pref(self) -> None:
        """Merger prompt contains valid canonical example with P:RecipeBot|PREF|H|D."""
        result = render_merger_prompt("", "validated")
        assert "P:RecipeBot|PREF|H|D" in result

    def test_canonical_example_does_not_use_invalid_aliases(self) -> None:
        """Canonical example does not use invalid aliases like PREFERENCE or GLOBAL as values."""
        result = render_merger_prompt("", "validated")
        if "Canonical Example" in result:
            example_start = result.find("Canonical Example")
            example_section = result[example_start:]
            if "Rules:" in example_section:
                example_section = example_section[: example_section.find("Rules:")]
            # Check that invalid aliases do NOT appear as values in data lines
            # The ## GLOBAL header is valid (section header format), but "GLOBAL|" as a value is not
            assert "GLOBAL|" not in example_section, "Example should use G, not GLOBAL"
            assert "PREFERENCE" not in example_section, "Example should use PREF, not PREFERENCE"
            assert "STABLE|" not in example_section, "Example should use D, not STABLE"
            assert "PROJECT|" not in example_section, "Example should use P:<name>, not PROJECT"
            assert "REPO|" not in example_section, "Example should use R:<name>, not REPO"
            assert "TEMPORARY|" not in example_section, "Example should use T, not TEMPORARY"


class TestRenderCompressorPrompt:
    """Tests for render_compressor_prompt."""

    def test_returns_string(self) -> None:
        """Each render function returns a string."""
        result = render_compressor_prompt("memory_full")
        assert isinstance(result, str)

    def test_contains_memory_full(self) -> None:
        """Each prompt contains its inserted input."""
        memory_full = "full memory content"
        result = render_compressor_prompt(memory_full)
        assert memory_full in result

    def test_contains_memory_prompt(self) -> None:
        """Compressor prompt contains # MEMORY_PROMPT."""
        result = render_compressor_prompt("memory_full")
        assert "# MEMORY_PROMPT" in result

    def test_no_unresolved_placeholders(self) -> None:
        """No prompt accidentally contains unresolved placeholder markers."""
        result = render_compressor_prompt("memory_full", "next context")
        unresolved = re.findall(r"\{[a-z_]+\}", result)
        assert not unresolved, f"Unresolved placeholders: {unresolved}"

    def test_empty_next_context_allowed(self) -> None:
        """Test empty next_context is allowed."""
        result = render_compressor_prompt("memory_full", "")
        assert isinstance(result, str)
        assert "memory_full" in result

    def test_next_context_inserted(self) -> None:
        """Next context is inserted when provided."""
        next_ctx = "next context here"
        result = render_compressor_prompt("memory_full", next_ctx)
        assert next_ctx in result

    def test_missing_memory_full_raises_value_error(self) -> None:
        """Missing memory_full raises ValueError."""
        with pytest.raises(ValueError, match="memory_full is required"):
            render_compressor_prompt(None, "next")  # type: ignore

    def test_contains_english_instruction_text(self) -> None:
        """Compressor prompt contains English instruction text."""
        result = render_compressor_prompt("memory_full")
        assert "You are a memory compressor" in result

    def test_contains_memory_full_delimiter(self) -> None:
        """Compressor prompt contains MEMORY_FULL delimiter block."""
        result = render_compressor_prompt("memory_full")
        assert "<<<MEMORY_FULL" in result
        assert "MEMORY_FULL>>>" in result

    def test_contains_next_context_delimiter(self) -> None:
        """Compressor prompt contains NEXT_CONTEXT delimiter block."""
        result = render_compressor_prompt("memory_full", "next context")
        assert "<<<NEXT_CONTEXT" in result
        assert "NEXT_CONTEXT>>>" in result

    def test_contains_empty_next_context_guidance(self) -> None:
        """Compressor prompt guides handling of empty NEXT_CONTEXT."""
        result = render_compressor_prompt("memory_full")
        assert "If NEXT_CONTEXT is empty" in result
        assert "general future chat" in result
        assert "keep broadly useful global entries" in result
        assert "high/medium priority project entries" in result
