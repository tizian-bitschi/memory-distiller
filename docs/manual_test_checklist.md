# Manual Test Checklist

Use this checklist to verify the app works from a fresh clone.

## Fresh Install

- [ ] Clone the repository
- [ ] Run `python -m pip install -e ".[dev]"`
- [ ] Verify installation completed without errors

## App Startup

- [ ] Run `streamlit run memory_distiller/app.py`
- [ ] App opens in browser without errors
- [ ] All six tabs are visible: Input, Extract, Validate, Merge, Compress, Export / Results
- [ ] Sidebar shows Mode selector, Model selector, Temperature, Thinking enabled, Reasoning effort

## Prompt-Only Workflow with Example Files

Find the example files in `examples/`:
- `examples/synthetic_chat_log.md`
- `examples/memory_full_before.md`

If no example files exist, create minimal synthetic content to test the pipeline.

### Input tab

- [ ] Paste synthetic_chat_log.md content in the chat log field
- [ ] Paste memory_full_before.md content in the existing memory field
- [ ] Optionally enter next context hint

### Extract tab

- [ ] Generate extractor prompt (button or auto-render in prompt-only mode)
- [ ] Paste mock extractor response
- [ ] Click "Parse Candidates"
- [ ] Verify candidates are parsed and displayed

### Validate tab

- [ ] Generate validator prompt
- [ ] Paste mock validator response
- [ ] Click "Parse Validated Candidates"
- [ ] Verify validated candidates appear with verdicts (KEEP, EDIT, DROP, ASK, CONFLICT)

### Merge tab

- [ ] Generate merger prompt
- [ ] Paste mock merger response
- [ ] Click "Parse Memory Document"
- [ ] Verify memory document is parsed and summary is shown

### Compress tab

- [ ] Generate compressor prompt
- [ ] Verify prompt is displayed (in prompt-only mode, no output parsing is available)

### Export / Results tab

- [ ] All four raw output areas are present
- [ ] "Download candidates.txt" button appears when candidates exist
- [ ] "Download validated_candidates.txt" button appears when validated candidates exist
- [ ] "Download memory_full.md" button appears when memory_full exists
- [ ] "Download memory_prompt.md" button appears when memory_prompt exists
- [ ] Downloads produce correct filenames and content

## API Mode

### Missing API key

- [ ] Set sidebar mode to "API"
- [ ] Do not set DEEPSEEK_API_KEY
- [ ] Click "Run extraction"
- [ ] Clear error message appears: "API key not found..."

### API key configured (manual test)

- [ ] Set DEEPSEEK_API_KEY in environment
- [ ] Set sidebar mode to "API"
- [ ] Configure model, temperature, thinking enabled, reasoning effort
- [ ] Run extraction — verify it completes without error
- [ ] Run validation — verify it completes without error
- [ ] Run merge — verify it completes without error
- [ ] Run compression — verify it completes without error

## File Upload

### Supported file types

- [ ] Upload a `.md` chat log file — file is read successfully
- [ ] Upload a `.txt` memory file — file is read successfully
- [ ] Upload a `.markdown` file — file is read successfully

### Unsupported file type

- [ ] Attempt to upload a `.pdf` file — app shows error: "Invalid file extension"
- [ ] Attempt to upload a `.csv` file — app shows error: "Invalid file extension"

## Error Resilience

- [ ] Paste a malformed LLM response in extract step — parse error is shown, app remains usable
- [ ] Paste a malformed LLM response in validate step — parse error is shown, app remains usable
- [ ] Paste a malformed LLM response in merge step — parse error is shown, app remains usable

## Privacy Behavior

- [ ] In prompt-only mode, no network requests are made
- [ ] In API mode, sidebar shows a warning that data is sent to the LLM provider
- [ ] No local files are created automatically by the app

## Session Behavior

- [ ] Refreshing the page clears session state (no persistent memory between sessions)
- [ ] Switching between tabs preserves entered data within the session