---
type: troubleshooting
feature: doc-gen-pipeline
depth: troubleshooting
generated_at: 2026-04-11T05:01:05.992103+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Troubleshoot doc gen pipeline

## Before you start

The doc gen pipeline generates documentation through three stages: outline creation, content writing, and review. Each stage calls an LLM with specific prompts and parameters. Issues typically occur at stage boundaries or when LLM responses don't match expected formats.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `generate_docs()` raises an exception | Check the target file exists and is readable |
| Empty or malformed outline | Verify `build_outline()` parameters: `doc_type`, `audience`, and `max_tokens` |
| Content generation fails | Confirm the outline from `build_outline()` is valid text, not empty |
| Review stage produces unchanged content | Check if `review_content()` received a complete draft, not a partial string |
| Pipeline stops mid-stage | Inspect LLM client connection and API rate limits |

## Step-by-step diagnosis

1. **Test each stage individually.**
   Run `build_outline()`, `write_content()`, and `review_content()` separately with the same parameters that failed in `generate_docs()`. This isolates which stage breaks.

2. **Validate your DocGenConfig.**
   Print the config object before passing it to `generate_docs()`. Confirm `model`, `max_tokens`, and other LLM parameters are set correctly.

3. **Check LLM responses.**
   Add logging to capture the raw responses from each stage. Look for:
   - Outline stage: structured headings and bullet points
   - Write stage: complete sections matching outline structure
   - Review stage: polished content with improvements

4. **Verify outline parsing.**
   Call `parse_outline_sections()` on your outline output. If it returns an empty list, the outline format doesn't match the expected structure with clear section headings.

5. **Test with minimal input.**
   Try `generate_docs()` with a simple source file (10-20 lines) and basic config. If this works, gradually add complexity until you reproduce the failure.

## Common fixes

- **Fix malformed outlines.** If `build_outline()` returns text without clear section headers, adjust the `doc_type` or `audience` parameters to get more structured output.

- **Increase token limits.** Set `max_tokens` higher in your `DocGenConfig` if content gets cut off mid-sentence. Start with 2048 for short docs, 4096 for longer ones.

- **Handle LLM client errors.** Wrap `generate_docs()` calls in try-catch blocks to handle API timeouts, rate limits, or authentication failures from the LLM service.

- **Validate file paths.** Use `pathlib.Path(target).exists()` to confirm source files exist before calling `generate_docs()`. Non-existent files cause immediate failures.

- **Reset client state.** If using a persistent LLM client, create a fresh client instance between pipeline runs to avoid connection issues.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
