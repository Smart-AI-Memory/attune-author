---
type: troubleshooting
feature: polish
depth: troubleshooting
generated_at: 2026-04-14T14:00:16.531656+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Troubleshoot polish

## Before you start

The polish feature improves generated template quality using LLM-powered rewrites. It applies template-specific system prompts and includes source summaries to keep content accurate and grounded.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `PolishError` exception | The error message for the specific failure reason and template type |
| Templates unchanged after polish | The `strict` parameter setting and `ATTUNE_AUTHOR_STRICT_POLISH` environment variable |
| Polish produces incorrect content | The source summary passed to `build_source_summary()` for completeness |
| LLM API failures | Network connectivity and Anthropic API credentials |

## Step-by-step diagnosis

1. **Reproduce with minimal input.**
   Create a simple test case using `polish_template()` with just the required parameters: `content`, `feature_name`, and `source_summary`. Use a basic template to isolate the polish logic from template complexity.

2. **Check the polish mode.**
   Verify whether strict mode is enabled by checking the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable. In strict mode, polish failures raise `PolishError`. In non-strict mode, the original content is returned silently.

3. **Examine the system prompt.**
   Call `get_system_prompt()` with your template type to see the exact instructions sent to the LLM. Template-specific prompts may have different requirements or restrictions.

4. **Validate the source summary.**
   Use `build_source_summary()` to generate the source information passed to the LLM. Incomplete or inaccurate summaries can lead to hallucinated content in the polished output.

## Common fixes

- **Set strict mode for debugging.** Export `ATTUNE_AUTHOR_STRICT_POLISH=1` to force `PolishError` exceptions instead of silent fallbacks, making failures visible during development.

- **Verify Anthropic API setup.** Ensure your API key is configured correctly. The polish feature uses Anthropic's Claude for the rewrite pass.

- **Update the source summary.** If polish removes or changes important details, expand the source summary by including more function signatures, class signatures, or module constants in the `build_source_summary()` call.

- **Check template type mapping.** Verify that your template type has a corresponding system prompt. Unknown types fall back to generic prompts that may not match your content structure.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
