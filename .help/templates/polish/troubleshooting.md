---
type: troubleshooting
feature: polish
depth: troubleshooting
generated_at: 2026-04-11T04:48:53.370835+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Troubleshoot polish

## Before you start

The polish feature rewrites auto-generated help templates using an LLM to improve quality and readability. It uses template-specific system prompts and source code summaries to guide the rewrite process.

## Symptom table

| If you observe | Check |
|----------------|-------|
| PolishError exception | Error message for specifics: API failures, strict mode violations, or prompt construction issues |
| Template content unchanged after polish | LLM response parsing in `polish_template()` — check if the response contains valid markdown |
| Wrong template style applied | Template type detection — verify the correct system prompt is selected by `get_system_prompt()` |
| Missing source information in output | Source summary construction in `build_source_summary()` — confirm all required metadata is included |

## Step-by-step diagnosis

1. **Reproduce with minimal input.**
   Create a simple test case with just the failing template content and feature name. Call `polish_template()` directly with `strict=True` to surface any hidden errors.

2. **Check the LLM API connection.**
   Verify your API credentials and network access. Run a basic LLM call outside the polish module to confirm the service is reachable.

3. **Examine the system prompt.**
   Call `get_system_prompt()` with your template type and inspect the returned prompt. Ensure it matches the expected format for your template category.

4. **Validate the source summary.**
   Use `build_source_summary()` to generate the source context separately. Check that all functions, classes, and module information are correctly captured.

5. **Enable strict mode.**
   Set `strict=True` when calling `polish_template()`. This surfaces PolishError exceptions that are normally caught and logged.

## Common fixes

- **Set API credentials.** Export `ANTHROPIC_API_KEY` in your environment:
  ```bash
  export ANTHROPIC_API_KEY=your_key_here
  ```

- **Add missing template type.** If you get an unknown template type error, add the new type to `get_system_prompt()`:
  ```python
  elif template_type == "your_new_type":
      return "Your system prompt here..."
  ```

- **Fix source summary data.** Ensure your source analysis provides complete function signatures and class information to `build_source_summary()`.

- **Handle network timeouts.** Add retry logic or increase timeout values if the LLM API is unreliable in your environment.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
