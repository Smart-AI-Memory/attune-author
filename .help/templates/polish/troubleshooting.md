---
type: troubleshooting
feature: polish
depth: troubleshooting
generated_at: 2026-04-14T16:05:11.147901+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Troubleshoot polish

## Before you start

The polish feature improves generated help templates using LLM rewrites. It applies type-specific system prompts and builds source-grounded summaries to ensure accuracy. When polish fails, the issue is typically with template content, LLM connectivity, or strict mode validation.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `PolishError` exception | The error message contains the feature name, template type, and specific failure reason |
| Silent failure with unchanged template | Return value of `polish_template()` - may return original content on non-strict failures |
| Wrong template type handling | Template frontmatter `type` field and the `template_type` parameter passed to `polish_template()` |
| Missing source context in output | Output of `build_source_summary()` with your module's classes and functions |

## Step-by-step diagnosis

1. **Reproduce with minimal input.**
   Create a simple test template with just the frontmatter block and a basic title. Call `polish_template()` with known-good parameters to isolate whether the issue is with your specific template or the polish system itself.

2. **Check the source summary.**
   Run `build_source_summary()` with your module's metadata and verify it contains the expected classes, functions, and docstrings. An incomplete summary leads to hallucinated content in the polished output.

3. **Validate strict mode behavior.**
   Test both `strict=True` and `strict=False` modes. In strict mode, `PolishError` exceptions surface immediately. In non-strict mode, failures may return the original template silently.

4. **Examine the system prompt.**
   Call `get_system_prompt(template_type)` with your template type to verify the correct prompt is loaded. Unsupported template types may fall back to generic prompts.

## Common fixes

- **Set the ATTUNE_AUTHOR_STRICT_POLISH environment variable** to control strict mode globally. Set to `'1'`, `'true'`, `'yes'`, or `'on'` to enable strict validation across all polish operations.

- **Verify template frontmatter format.** Ensure your template has a valid YAML frontmatter block with `---` delimiters and a `type` field that matches the `template_type` parameter.

- **Check LLM service availability.** Polish requires an active connection to Anthropic's API. Network issues or API key problems surface as exceptions during the polish pass.

- **Update template type support.** If you're using a custom template type, ensure `get_system_prompt()` has a corresponding prompt definition. Missing types fall back to generic behavior.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
