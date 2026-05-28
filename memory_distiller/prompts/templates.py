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
- Do NOT use: GLOBAL, PROJECT, REPO, TEMPORARY. Use: G, P:<name>, R:<name>, T.
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

VERDICT:
KEEP = accept
EDIT = accept, but corrected
DROP = do not accept
ASK = user should be asked
CONFLICT = conflict must be checked manually

INVALID-ALIAS WARNING:
- Do NOT use: GLOBAL, PROJECT, REPO, TEMPORARY. Use: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Example (valid output):
M1|KEEP|ADD|-|P:RecipeBot|RULE|H|D|All recipes in RecipeBot must be vegetarian.|User explicitly asked to remember this for RecipeBot.|Well-supported project rule.
M2|EDIT|ADD|-|P:RecipeBot|PREF|M|D|RecipeBot should use metric units by default.|User asked to use metric units.|Better represented as a preference than a hard rule.
M3|DROP|IGNORE|-|T|FACT|L|T|The user is only testing today.|User said this should not be remembered permanently.|Temporary detail.

Rules:
- For KEEP or EDIT, STATEMENT must be final usable memory text.
- For DROP, briefly explain in REASON why.
- For ASK, formulate STATEMENT as a concrete check question.
- For CONFLICT, briefly name the conflict.
- Do not output a general summary."""

MERGER_V1 = """You are a memory merger.

Goal:
Create an updated memory file from existing memory and validated candidates.

Existing Memory:
<<<MEMORY
{existing_memory}
MEMORY>>>

Validated Candidates:
<<<VALIDATED
{validated_candidates}
VALIDATED>>>

Task:
1. Take over KEEP and EDIT entries.
2. Apply UPDATE to existing entries.
3. Remove or mark DEPRECATE entries as obsolete.
4. Do not take over DROP entries.
5. Do not take over ASK entries as memory; list them separately under "Offene Klärungen".
6. Merge duplicates.
7. Keep each memory entry atomic.
8. Keep evidence but shorten to the essential.
9. Sort by scope: GLOBAL, then PROJECTS, then REPOS, then TEMPORARY, then DEPRECATED.
10. Use a compact, manually maintainable format.

Output-Format:

# MEMORY_FULL

## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS

INVALID-ALIAS WARNING:
- Do NOT use: GLOBAL, PROJECT, REPO, TEMPORARY. Use: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Example (valid output):
# MEMORY_FULL

## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
G|RULE|H|D|Answer in German by default.|User preference.

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
P:RecipeBot|PREF|H|D|Use metric units in recipes.|User request.

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS

Rules:
- No JSON output.
- No long explanations.
- No normal summaries.
- STATEMENT must be directly usable as future context."""

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
