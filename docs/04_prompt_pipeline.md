# Prompt Pipeline

## Goal

The prompt pipeline produces verifiable memory entries from chat logs, not a normal summary text.

The MVP starts with four steps:

```text
Chat Log → Extractor → Validator → Merger → Compressor
```

An optional fifth step may be added:

```text
ASK/CONFLICT → Conflict Clarifier → User Response → Memory Update
```

## Step 1: Extractor

Purpose:

- Find candidates for new or changed memory entries.
- Distinguish between global, project-specific, and temporary context.
- Give special attention to user corrections.

Input:

- Chat log
- optional existing memory

Output:

```text
ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

Quality Criteria:

- No assistant suggestions without user confirmation
- No normal summaries
- No overly broad generalizations
- Atomic entries

## Step 2: Validator

Purpose:

- Critically review extractor candidates.
- Discard incorrect, overly general, or poorly supported entries.
- Correct scope and stability.

Output:

```text
ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

Validator Rule:

High precision is more important than high recall. Better to store nothing than to store incorrect permanent memory.

## Step 3: Merger

Purpose:

- Merge existing memory and validated candidates into a new `memory_full.md`.
- Make updates, deprecations, and conflicts visible.
- Collect open questions separately.

Output:

```text
# MEMORY_FULL
...
```

## Step 4: Compressor

Purpose:

- Produce a compact prompt block from `memory_full.md`.
- Remove evidence.
- Omit irrelevant project rules.
   - Empty NEXT_CONTEXT means general-purpose compression; keep broadly useful project entries.
- Produce no more than about 20-25 lines.

Output:

```text
# MEMORY_PROMPT
...
```

## Prompt: Extractor with Existing Memory

```text
You are a memory extractor comparing a new chat log with existing memory.

Goal:
Extract new, changed, or conflicting memory candidates from the chat.

Existing Memory:
<<<MEMORY
[INSERT EXISTING MEMORY HERE]
MEMORY>>>

New Chat Log:
<<<CHAT
[INSERT CHAT LOG HERE]
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

Do not output any explanation outside the candidate list.
```

## Prompt: Validator

```text
You are a strict memory validator.

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
[INSERT EXISTING MEMORY HERE]
MEMORY>>>

Chat Log:
<<<CHAT
[INSERT CHAT LOG HERE]
CHAT>>>

Memory Candidates:
<<<CANDIDATES
[INSERT CANDIDATES FROM PROMPT 1 OR 2 HERE]
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

Rules:
- For KEEP or EDIT, STATEMENT must be final usable memory text.
- For DROP, briefly explain in REASON why.
- For ASK, formulate STATEMENT as a concrete check question.
- For CONFLICT, briefly name the conflict.
- Do not output a general summary.
```

## Prompt: Merger

```text
You are a memory merger.

Goal:
Create an updated memory file from existing memory and validated candidates.

Existing Memory:
<<<MEMORY
[INSERT EXISTING MEMORY HERE]
MEMORY>>>

Validated Candidates:
<<<VALIDATED
[INSERT VALIDATOR OUTPUT HERE]
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
9. Sort entries into sections in this order: ## GLOBAL, ## PROJECTS, ## REPOS, ## TEMPORARY, ## DEPRECATED.
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
- Do NOT use these as SCOPE field values: GLOBAL, PROJECT, REPO, TEMPORARY.
  Use SCOPE values only as: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.
- Note: Section headers such as ## GLOBAL and ## TEMPORARY are allowed in MEMORY_FULL.

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
- STATEMENT must be directly usable as future context.
```

## Prompt: Compressor

```text
You are a memory compressor for LLM prompts.

Goal:
Create from the full memory a very compact context block that can be inserted at the beginning of new chats.

Full Memory:
<<<MEMORY_FULL
[INSERT MEMORY_FULL HERE]
MEMORY_FULL>>>

Optional target context of the next chat:
<<<NEXT_CONTEXT
[INSERT BRIEF DESCRIPTION OF WHAT THE NEXT CHAT IS ABOUT; LEAVE EMPTY IF UNKNOWN]
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
- Output only the final prompt block.
```

## Prompt Versioning

Prompt templates should be versioned in code, e.g.:

```text
extractor_v1
validator_v1
merger_v1
compressor_v1
```

Each produced output should later optionally be able to store which prompt version created it. For the MVP, a visible constant in the prompt template is sufficient.