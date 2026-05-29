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

- Merge existing memory and validated candidates into a structured merge plan.
- The merge plan is then applied deterministically by Python to render `MEMORY_FULL`.
- Make updates, deprecations, and conflicts visible.
- Collect open questions separately.

Output:

```text
ID|MERGE_DECISION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

MERGE_DECISION values:

| Value | Meaning |
|-------|---------|
| APPLY_ADD | Add as new memory entry |
| APPLY_UPDATE | Update existing entry at TARGET |
| APPLY_DEPRECATE | Mark existing entry at TARGET as deprecated |
| SKIP_DROP | Skip this candidate (drop it) |
| ADD_OPEN_QUESTION | Add to open questions list |

Note: The Merger outputs a structured merge plan. Python applies the plan deterministically and renders `MEMORY_FULL`. This avoids LLM formatting errors and ensures consistent output.

Canonical examples:

```text
M1|APPLY_ADD|-|G|RULE|H|D|Answer in German by default.|User preference.|Reusable global rule.
M2|APPLY_UPDATE|M3|G|PREF|H|D|Use metric units by default.|User requested metric.|Updated preference.
M3|APPLY_DEPRECATE|M5|G|RULE|M|D|Old rule text.|Superseded by new approach.|Outdated.
M4|SKIP_DROP|-|T|FACT|L|T|Temporary testing note.|Not worth keeping.|Too trivial.
M5|ADD_OPEN_QUESTION|-|P:RecipeBot|RULE|H|M|Should RecipeBot enforce strict ingredient checking?|Needs user decision.|Conflict between two proposed approaches.
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

## Prompt: Merger (MERGER_V1)

```text
You are a memory merger.

Goal:
Create a structured merge plan from existing memory and validated candidates.
You do NOT render MEMORY_FULL. You only output merge decisions.
The application will render the final MEMORY_FULL deterministically.

Existing Memory:
<<<MEMORY
[INSERT EXISTING MEMORY HERE]
MEMORY>>>

Validated Candidates:
<<<VALIDATED
[INSERT VALIDATOR OUTPUT HERE]
VALIDATED>>>

Task:
1. Decide whether to APPLY_ADD each KEEP/EDIT candidate as new entry.
2. Decide whether to APPLY_UPDATE existing entries based on UPDATE candidates.
3. Decide whether to APPLY_DEPRECATE entries marked DEPRECATE in candidates.
4. SKIP_DROP entries that should not be added.
5. ADD_OPEN_QUESTION for ASK entries; do not add them as memory.
6. Do not output MEMORY_FULL yourself.

Output-Format:

ID|MERGE_DECISION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

Fields:
- ID: Candidate ID or new ID for APPLY_ADD
- MERGE_DECISION: APPLY_ADD, APPLY_UPDATE, APPLY_DEPRECATE, SKIP_DROP, ADD_OPEN_QUESTION
- TARGET: For APPLY_UPDATE/DEPRECATE, ID of existing entry; for APPLY_ADD: -
- SCOPE: G, P:<name>, R:<name>, T
- TYPE: RULE, PREF, FACT, DECISION, AVOID, STYLE, SOURCE, TERM, TASK
- PRIO: H, M, L
- STABILITY: D, M, T
- STATEMENT: Final memory text (for APPLY_ADD, APPLY_UPDATE) or question (for ADD_OPEN_QUESTION)
- EVIDENCE: Supporting evidence, shortened
- REASON: Why this decision was made

INVALID-ALIAS WARNING:
- Do NOT use these as SCOPE field values: GLOBAL, PROJECT, REPO, TEMPORARY.
  Use SCOPE values only as: G, P:<name>, R:<name>, T.
- Do NOT use: PREFERENCE. Use: PREF.
- Do NOT use: HIGH, MEDIUM, LOW. Use: H, M, L.
- Do NOT use: STABLE, DURABLE. Use: D, M, T.

Canonical Example (valid output):
M1|APPLY_ADD|-|G|RULE|H|D|Answer in German by default.|User preference.|Reusable global rule.
M2|APPLY_UPDATE|M3|G|PREF|H|D|Use metric units by default.|User requested metric.|Updated preference.
M3|APPLY_DEPRECATE|M5|G|RULE|M|D|Old rule text.|Superseded by new approach.|Outdated.
M4|SKIP_DROP|-|T|FACT|L|T|Temporary testing note.|Not worth keeping.|Too trivial.
M5|ADD_OPEN_QUESTION|-|P:RecipeBot|RULE|H|M|Should RecipeBot enforce strict ingredient checking?|Needs user decision.|Conflict between two proposed approaches.

Rules:
- Do NOT output MEMORY_FULL.
- Do NOT output section headers like ## GLOBAL.
- Output only merge decision lines.
- No JSON output.
- No long explanations.
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
merger_v1 (MERGER_V1)
compressor_v1
```

Each produced output should later optionally be able to store which prompt version created it. For the MVP, a visible constant in the prompt template is sufficient.