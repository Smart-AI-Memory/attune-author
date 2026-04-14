---
type: error
feature: polish
depth: error
generated_at: 2026-04-14T16:04:42.372081+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish errors

Template polishing failures occur when the LLM-based rewrite pass cannot successfully improve auto-generated help documentation.

## Common error signatures

- `PolishError: Polish pass failed for {feature_name} (type={template_type}): {error_details}`

This exception is raised when `polish_template()` runs in strict mode and the LLM polish operation fails.

## Where errors originate

Polish failures typically emerge from these functions:

- `polish_template()` — The main polishing function that coordinates the LLM rewrite. When strict mode is enabled, LLM failures raise `PolishError` instead of returning the original content.
- `build_source_summary()` — Constructs the source information that guides the polish pass. Malformed summaries can lead to poor LLM responses.
- `get_system_prompt()` — Retrieves template-type-specific prompting instructions. Missing or invalid template types may cause downstream failures.

## How to diagnose

1. **Check strict mode configuration.** Strict mode is controlled by the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable. When enabled, polish failures raise exceptions instead of falling back gracefully. Verify whether strict mode is intended for your use case.

2. **Examine the feature name and template type.** The `PolishError` message includes both values passed to `polish_template()`. Invalid template types or malformed feature names often indicate upstream issues in template generation.

3. **Review the source summary content.** Run `build_source_summary()` with your module data to verify it produces coherent, well-structured output. Incomplete or corrupted source information leads to poor polish results.

4. **Test with a simpler template.** If the polish pass fails consistently, try with minimal template content to isolate whether the issue is with the LLM service, the prompt construction, or the specific template content.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
