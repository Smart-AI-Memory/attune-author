---
type: error
feature: polish
depth: error
generated_at: 2026-04-14T13:59:49.722471+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Polish errors

Polish failures occur when the LLM-powered template rewriting process encounters issues with the AI service, input validation, or strict mode enforcement.

## Common error signatures

- `PolishError: Polish pass failed for {feature_name} (type={template_type}): {details}` — Raised when `polish_template()` fails in strict mode
- `AnthropicCallError` — Communication failures with the Anthropic API during LLM processing
- `ValueError` — Invalid template type passed to `get_system_prompt()` or malformed content structure
- `KeyError` — Missing required fields when building source summaries

## Where errors originate

Polish failures typically stem from three main functions:

- `polish_template()` — Handles LLM communication and strict mode validation. Most `PolishError` exceptions originate here when the AI service returns unusable output or fails entirely.
- `get_system_prompt()` — Validates template types against known prompt templates. Raises `ValueError` for unsupported template kinds.
- `build_source_summary()` — Processes class and function metadata into prompt-ready format. Can fail on malformed input dictionaries or missing required keys.

## How to diagnose

1. **Check strict mode configuration.** If you see `PolishError` exceptions, verify the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable. When strict mode is enabled, polish failures halt the process instead of returning unpolished content.

2. **Examine the template type.** `ValueError` from `get_system_prompt()` indicates an unsupported template type was requested. Valid types have corresponding system prompts defined in the prompts module.

3. **Verify API connectivity.** `AnthropicCallError` suggests network issues or API authentication problems. Check your Anthropic API key and network connection.

4. **Inspect source summary inputs.** If `build_source_summary()` fails, examine the class and function dictionaries being passed. Each should contain required string keys for names, docstrings, and signatures.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
