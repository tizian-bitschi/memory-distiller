# Usage Guide

## Local Installation

```bash
python -m pip install -e ".[dev]"
```

## Starting the App

```bash
streamlit run memory_distiller/app.py
```

The app opens in your browser with a tabbed interface: Input, Extract, Validate, Merge, Compress, Export / Results.

## Modes

The sidebar lets you choose between two modes:

**Prompt-only** — Generate prompts manually, paste LLM responses. No API key needed.

**API** — The app calls DeepSeek directly. Requires the `DEEPSEEK_API_KEY` environment variable to be set. If the key is missing, the app shows a clear error when you try to run a step.

## Workflow

### 1. Input

Go to the Input tab. Paste your chat log and optionally an existing memory file.

You can paste your chat log directly into the text area, or upload a `.txt`, `.md`, `.markdown`, `.html`, or `.htm` file via the Chat Log file uploader. ChatGPT HTML exports (`.html`, `.htm`) are automatically converted to plain-text chat logs in memory.

The Existing Memory upload only accepts plain text and Markdown memory files (`.txt`, `.md`, `.markdown`).

Uploaded files are read into the current session only and are never written to disk.

Optionally provide a "Next context hint" to guide the compression step later.

### 2. Extract

Go to the Extract tab.

In **Prompt-only mode**: Click to generate the extractor prompt, then paste the LLM response and parse the candidates.

In **API mode**: Click "Run extraction" to call DeepSeek. The candidates appear automatically.

### 3. Validate

Go to the Validate tab.

Paste the LLM response from your validator or run it via API. Parsing produces validated candidates with verdicts.

### 4. Merge

Go to the Merge tab.

Paste the LLM merge plan response or run it via API. The app parses the merge plan, applies it to existing memory, and renders the final `MEMORY_FULL` deterministically.

### 5. Compress

Go to the Compress tab.

In **Prompt-only mode**: The compressor prompt is generated. Paste the LLM response manually (the prompt display is the only output in this mode).

In **API mode**: Click "Run compression" to generate the memory prompt block.

### 6. Export / Results

Go to the Export / Results tab to see all raw outputs and download them:

- `candidates.txt` — raw extractor output
- `validated_candidates.txt` — raw validator output
- `memory_full.md` — full memory document
- `memory_prompt.md` — compressed prompt block

Downloads are generated in memory. Nothing is saved automatically to disk.

## Interpreting Candidates

### Verdicts (from validation)

| Verdict | Meaning |
|---------|---------|
| KEEP | Candidate is valid as-is |
| EDIT | Candidate needs changes before keeping |
| DROP | Candidate should be discarded |
| ASK | Requires human decision |
| CONFLICT | Conflicts with existing memory |

### Actions (on candidates)

| Action | Meaning |
|--------|---------|
| ADD | New memory entry to add |
| UPDATE | Existing entry to modify |
| DEPRECATE | Old entry to mark as superseded |
| IGNORE | Skip this candidate |
| CONFLICT | Cannot resolve automatically |
| ASK | Needs human review |

## Handling Parse Errors

If parsing fails, the app shows an error with details. Common causes:

- LLM output does not follow the pipe-delimited format expected by the parser
- Malformed lines, missing required fields, or invalid MERGE_DECISION values
- For merge plans: invalid TARGET references or unrecognized scope values

To fix: review the LLM output, correct the format, and re-paste. The app remains usable after parse errors.

**Repairing common enum aliases**: The Extract, Validate, and Merge tabs include a "Repair common enum aliases" button. This converts known aliases to their canonical forms (PREFERENCE→PREF, GLOBAL→G, PROJECT:X→P:X, HIGH→H, STABLE→D, etc.). Free-text fields such as STATEMENT, EVIDENCE, and REASON are never modified. Only known aliases are repaired; unknown values still cause parse failures and must be corrected manually.

## API Usage and Cost Transparency

When running in **API mode**, the app shows estimated token usage and cost per pipeline step. After each API call (Extract, Validate, Merge, Compress), an expandable "Usage & Cost" section appears with:

- **Model** used for the call
- **Prompt tokens** — total input tokens
- **Cache hit tokens** — tokens served from cache (lower cost)
- **Cache miss tokens** — tokens not in cache (standard cost)
- **Completion tokens** — output tokens
- **Reasoning tokens** — thinking/reasoning tokens (when returned by the model)
- **Total tokens** — overall token count
- **Estimated cost in USD**

### Cost Estimates

Costs are calculated from manually configured DeepSeek pricing and may differ if the provider changes prices. The estimate uses:

- `deepseek-v4-flash` — input cache hit: $0.0028 per 1M tokens, cache miss: $0.14 per 1M, output: $0.28 per 1M
- `deepseek-v4-pro` — input cache hit: $0.003625 per 1M tokens, cache miss: $0.435 per 1M, output: $0.87 per 1M

If the API response does not include cache hit/miss breakdown, all prompt tokens are treated as cache miss and a fallback note is shown.

### Run-Level Summary

The **Export / Results** tab shows an aggregated usage summary and total estimated cost across all pipeline steps that ran in API mode.

### DeepSeek Balance Check

In API mode, the sidebar includes a **"Check DeepSeek Balance"** button. Clicking it fetches your current account balance (requires `DEEPSEEK_API_KEY`). The balance shows:

- Total balance per currency
- Granted balance (promotional credits)
- Topped-up balance (purchased credits)

The balance is **not** checked automatically — you must click the button. Balance data is kept in session state only and is not persisted.

### Important Notes

- All cost figures are **estimates** for transparency, not exact billing amounts.
- Your **API key is never shown** in the UI or stored in the app.
- Usage and balance data are kept **in session state only** and disappear when you refresh the page.
- No usage or balance data is written to disk.

## Prompt Token Transparency

Each pipeline step (Extract, Validate, Merge, Compress) shows an **estimated** prompt/request token count before the API call. The estimate includes:

- **System prompt** — the fixed instructions guiding the model
- **Rendered prompt** — your chat log, existing memory, and step context combined

The estimate is a simple heuristic (character count ÷ 4) and is labeled as "estimated". It **may differ** from the provider-reported token count.

**After each API call**, the app also shows **provider-reported usage** when available (e.g., from DeepSeek's response metadata). Provider-reported figures are:

- More accurate than estimates
- A better source for actual billing and cost tracking
- Shown alongside the estimate for comparison
- The basis for cost calculations in the Usage & Cost section

**Delta display**: When both estimate and provider-reported usage are available, the app shows the difference so you can see how the estimate compared to reality.

**No token data is persisted**. All token counts exist only in the current session and are cleared when you refresh or close the app.

## Privacy Notes

**Prompt-only mode**: Your data stays in the browser session. Nothing is sent to any external service.

**API mode**: Chat log, existing memory, and intermediate results are sent to DeepSeek for processing. Your privacy depends on the chosen provider's policies. The app warns you about this in the sidebar when API mode is active.