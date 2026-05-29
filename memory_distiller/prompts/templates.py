# ruff: noqa: E501
"""Prompt template constants for Memory Distiller."""

EXTRACTOR_V1 = """You are a memory extractor comparing a new chat log with existing memory.

Goal:
Extract new, changed, or conflicting memory candidates from the chat.

Existing Memory:
<<<MEMORY
{existing_memory}
MEMORY>>>

New Chat Log:
<<<CHAT
{chat_log}
CHAT>>>

Task:
1. Find new reusable rules, preferences, project facts, decisions, avoidance rules, terminology, and open tasks.
2. Check whether existing memory entries should be updated, weakened, replaced, or deleted.
3. Do not store temporary details as permanent.
4. Do not store assistant suggestions unless confirmed by the user.
5. Mark unclear cases as ASK.
6. Mark conflicts as CONFLICT.
7. Avoid duplicates to existing memory.

Output-Format:
Output only lines in this format:

ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

Legend:
ACTION = ADD, UPDATE, DEPRECATE, IGNORE, CONFLICT, ASK
TARGET = ID or short text of affected existing memory entry; for ADD: -
SCOPE = G or P:<project-name> or R:<repo/codebase> or T
TYPE = RULE, PREF, FACT, DECISION, AVOID, STYLE, SOURCE, TERM, TASK, CONFLICT
PRIO = H, M, L
STABILITY = D, M, T

Evaluation Criteria:
- High precision is more important than high recall.
- Better to mark a doubtful entry as ASK than to store it incorrectly.
- Use global rules only when they truly apply across projects.
- Always label project rules with the project name.
- Do not phrase statements about the user in unnecessarily personal ways.
- Include sensitive information only when it appears to be explicitly permanently relevant.

INVALID-ALIAS WARNING:
- Do NOT use these as SCOPE field values: GLOBAL, PROJECT, REPO, TEMPORARY.
  Use SCOPE values only as: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Example (valid output):
M1|ADD|-|P:RecipeBot|RULE|H|D|All recipes in RecipeBot must be vegetarian.|User explicitly asked to remember this for RecipeBot.|Reusable project rule.
M2|IGNORE|-|T|FACT|L|T|The user is only testing today.|User said this should not be remembered permanently.|Temporary detail.

Do not output any explanation outside the candidate list."""

VALIDATOR_V1 = """You are a strict memory validator.

Task:
Check the following memory candidates against the chat log and existing memory.

Remove, weaken, or correct candidates if they:
- are not sufficiently supported
- generalize too much
- were only asserted by the assistant
- are temporary but marked as permanent
- mix multiple statements
- are redundant to existing memory
- are wrongly scoped, e.g., global instead of project-specific
- formulate a preference as a hard rule
- store a one-time situation as a permanent rule
- contain sensitive or unnecessarily personal information

Existing Memory:
<<<MEMORY
{existing_memory}
MEMORY>>>

Chat Log:
<<<CHAT
{chat_log}
CHAT>>>

Memory Candidates:
<<<CANDIDATES
{candidates}
CANDIDATES>>>

Output-Format:
Output only validated lines in this format:

ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

IMPORTANT: Every output line MUST include VERDICT as the second column. Do NOT output extractor candidate format. A line like `M1|ADD|-|...` is invalid here because it is missing VERDICT. Use `M1|KEEP|ADD|-|...` or another valid verdict.

INVALID (extractor candidate format, 10 columns, missing VERDICT):
M1|ADD|-|P:RecipeBot|RULE|H|D|All recipes vegetarian.|User asked.|Reusable project rule.

VALID (validator output, 11 columns, with VERDICT):
M1|KEEP|ADD|-|P:RecipeBot|RULE|H|D|All recipes vegetarian.|User asked.|Reusable project rule.

VERDICT:
KEEP = accept
EDIT = accept, but corrected
DROP = do not accept
ASK = user should be asked
CONFLICT = conflict must be checked manually

INVALID-ALIAS WARNING:
- Do NOT use these as SCOPE field values: GLOBAL, PROJECT, REPO, TEMPORARY.
  Use SCOPE values only as: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Example (valid output):
M1|KEEP|ADD|-|P:RecipeBot|RULE|H|D|All recipes in RecipeBot must be vegetarian.|User explicitly asked to remember this for RecipeBot.|Well-supported project rule.
M2|EDIT|ADD|-|P:RecipeBot|PREF|H|D|RecipeBot should use metric units by default.|User asked to use metric units.|Better represented as a preference/default than a hard rule.
M3|DROP|IGNORE|-|T|FACT|L|T|The user is only testing today.|User said this should not be remembered permanently.|Temporary detail.

Guidance for TYPE classification:
- Use TYPE = PREF for preferences, defaults, stylistic tendencies, and soft conventions.
- Use TYPE = RULE only for hard constraints, explicit must/never/always behavior, safety constraints, or explicit technical/storage requirements.

Temporary-Detail Boundary Guidance:
- A user sentence like "do not remember this" may apply only to the nearest or explicitly referenced temporary detail.
- Do not retroactively drop earlier explicit reusable project instructions unless the user clearly says those instructions should not be remembered.
- If a chat contains both reusable instructions and a later temporary-test statement, keep the reusable instructions and drop only the temporary test detail.

Example input:
User: For RecipeBot, use friendly concise recipe text. Today I am only testing the memory pipeline; do not remember that.

Expected behavior:
- KEEP the RecipeBot style instruction.
- DROP the temporary pipeline-test fact.

Contradictory Verdict/Action Guidance:
- Do not emit KEEP|IGNORE.
- Do not emit EDIT|IGNORE.
- For ACTION=IGNORE, use VERDICT=DROP unless the candidate must become ASK or CONFLICT.
- KEEP and EDIT are only for entries that will be carried forward as memory.
- DROP is the normal verdict for candidates that should not be carried forward.

Invalid:
M8|KEEP|IGNORE|-|T|FACT|L|T|The user is only testing today.|User said not to remember this.|Temporary detail.

Valid:
M8|DROP|IGNORE|-|T|FACT|L|T|The user is only testing today.|User said not to remember this.|Temporary detail.

Existing-Memory Update Guidance:
- If a candidate refines or concretizes an existing memory entry, prefer EDIT|UPDATE over adding a redundant new memory entry.
- A storage preference like "file-based storage" refined into "Markdown files in repo, no DB for MVP" should become an update/decision rather than a duplicate preference.

Existing memory:
P:RecipeBot|PREF|M|D|RecipeBot should prefer simple file-based storage over database complexity.|Earlier project direction.

Candidate:
M6|ADD|-|P:RecipeBot|PREF|M|D|Store recipes as Markdown files in the repository.|User asked for Markdown files and no database for MVP.|Storage preference.

Expected:
M6|EDIT|UPDATE|RecipeBot should prefer simple file-based storage over database complexity.|P:RecipeBot|DECISION|H|M|RecipeBot should store recipes as Markdown files in the repository for the MVP and avoid a database for now.|User asked for Markdown files and said no database is needed for the MVP.|Refines existing storage preference into a concrete MVP decision.

Rules:
- For KEEP or EDIT, STATEMENT must be final usable memory text.
- For DROP, briefly explain in REASON why.
- For ASK, formulate STATEMENT as a concrete check question.
- For CONFLICT, briefly name the conflict.
- Do not output a general summary."""

MERGER_V1 = """You are a memory merger.

Goal:
Create a merge plan for updating memory from existing memory and validated candidates.

You do NOT render MEMORY_FULL. You only output merge decisions. The application will render the final MEMORY_FULL deterministically.

Existing Memory:
<<<MEMORY
{existing_memory}
MEMORY>>>

Validated Candidates:
<<<VALIDATED
{validated_candidates}
VALIDATED>>>

Task:
1. Take over KEEP and EDIT entries via APPLY_ADD.
2. Apply UPDATE to existing entries via APPLY_UPDATE.
3. Remove or mark DEPRECATE entries as obsolete via APPLY_DEPRECATE.
4. Do not take over DROP entries - use SKIP_DROP.
5. Do not take over ASK entries as memory - use ADD_OPEN_QUESTION instead.
6. Merge duplicates - skip duplicate statements.
7. Keep evidence but shorten to the essential.
8. Keep evidence but shorten to the essential.
9. Sort entries into sections: G (global), P:<project>, R:<repo>, T (temporary).

Output-Format:
ID|MERGE_DECISION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

MERGE_DECISION values:
- APPLY_ADD: add new memory entry
- APPLY_UPDATE: update existing entry (target = statement to find)
- APPLY_DEPRECATE: mark entry as deprecated (target = statement to find, reason = deprecation reason)
- SKIP_DROP: skip this candidate
- ADD_OPEN_QUESTION: add to open questions (statement = question, reason = why it matters)

INVALID-ALIAS WARNING:
- Do NOT use these as SCOPE field values: GLOBAL, PROJECT, REPO, TEMPORARY.
  Use SCOPE values only as: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Examples:

APPLY_ADD (new global rule):
M1|APPLY_ADD|-|G|RULE|H|D|Answer in German by default.|User preference.|German as default language.

APPLY_UPDATE (update existing project preference):
M2|APPLY_UPDATE|RecipeBot should prefer simple file-based storage.|P:RecipeBot|PREF|H|D|RecipeBot should store recipes as Markdown files in the repository for the MVP.|User asked for Markdown files.|Refines storage preference.

SKIP_DROP (candidate should not be memorized):
M3|SKIP_DROP|-|T|FACT|L|T|The user is only testing today.|User said not to remember.|Temporary detail.

ADD_OPEN_QUESTION (user needs to clarify):
M4|ADD_OPEN_QUESTION|-|P:RecipeBot|RULE|H|M|Should RecipeBot support other languages for recipes?|Multilingual recipe support is not yet decided.|Needs user decision.

Rules:
- No JSON output.
- No markdown MEMORY_FULL output.
- No long explanations.
- No summary sections.
- STATEMENT must be directly usable as future context.
- Do not output any explanation outside the merge plan format."""

COMPRESSOR_V1 = """You are a memory compressor for LLM prompts.

Goal:
Create from the full memory a very compact context block that can be inserted at the beginning of new chats.

Full Memory:
<<<MEMORY_FULL
{memory_full}
MEMORY_FULL>>>

Optional target context of the next chat:
<<<NEXT_CONTEXT
{next_context}
NEXT_CONTEXT>>>

Task:
1. Remove evidence.
2. Remove temporary, deprecated, and irrelevant entries.
3. Keep global high-priority rules.
4. Keep project-related entries only if they fit the target context.
   - If NEXT_CONTEXT is empty or whitespace-only, assume a general future chat. In that case, keep broadly useful global entries and high/medium priority project entries instead of dropping project context.
   - Only omit project entries when a non-empty NEXT_CONTEXT clearly makes them irrelevant.
5. Formulate extremely compact.
6. No full sentences when bullet points suffice.
7. Maximum 25 lines.
8. Prioritize rules that concretely change assistant behavior.
9. No private details without utility value.
10. No repetitions.

Output-Format:

# MEMORY_PROMPT
Beachte dauerhaft:
- ...

Projektkontext, falls relevant:
- ...

Arbeitsweise:
- ...

Nicht tun:
- ...

Rules:
- No evidence.
- No meta explanation.
- No JSON output.
- Output only the final prompt block."""
