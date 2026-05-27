# Memory Distiller - Synthetic Examples

These files are synthetic fictional examples for testing the Memory Distiller MVP pipeline.

## Scenario

**RecipeBot** - a fictional recipe assistant project. The example demonstrates extracting user preferences from a chat log and merging them with existing memory.

## Files

| File | Purpose |
|------|---------|
| `synthetic_chat_log.md` | Input: fictional chat transcript showing user preferences |
| `memory_full_before.md` | Input: existing memory state before processing |
| `extractor_candidates.txt` | Expected output from Extract step |
| `validated_candidates.txt` | Expected output from Validate step |
| `memory_full_after.md` | Expected output from Merge step |
| `memory_prompt.md` | Expected output from Compress step (prompt-only mode) |

## How to Use

1. Open the Streamlit app: `streamlit run app.py`
2. In the **Input** tab:
   - Paste/upload `synthetic_chat_log.md` as the chat log
   - Paste/upload `memory_full_before.md` as existing memory
3. Run the pipeline steps:
   - **Extract** → generates extractor candidates
   - **Validate** → filters/refines candidates
   - **Merge** → integrates into memory structure
   - **Compress** → creates prompt-only output (or use API mode for full compression)
4. Compare results with the example files:
   - Extractor output should resemble `extractor_candidates.txt`
   - Validator output should resemble `validated_candidates.txt`
   - Merger output should resemble `memory_full_after.md`
   - Compressor output should resemble `memory_prompt.md`
5. Download results in the **Export / Results** tab

## Note

All content is fictional. No real personal data, chat logs, or secrets are used. This is a demonstration scenario for testing the Memory Distiller pipeline without exposing any private information.