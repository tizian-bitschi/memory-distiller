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

You can also upload `.txt`, `.md`, or `.markdown` files using the file uploaders. Uploaded files go into the session only and are never written to disk.

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

Paste the LLM response from your merger or run it via API. Parsing produces a memory document.

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
- Malformed lines or missing required fields

To fix: review the LLM output, correct the format, and re-paste. The app remains usable after parse errors.

## Privacy Notes

**Prompt-only mode**: Your data stays in the browser session. Nothing is sent to any external service.

**API mode**: Chat log, existing memory, and intermediate results are sent to DeepSeek for processing. Your privacy depends on the chosen provider's policies. The app warns you about this in the sidebar when API mode is active.