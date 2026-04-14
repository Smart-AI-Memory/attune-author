---
type: faq
feature: polish
depth: faq
generated_at: 2026-04-14T14:00:32.501462+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Polish FAQ

## What is polish?

Polish improves auto-generated help templates by rewriting them with an LLM that understands different template types and has access to your source code context.

## When should I use polish?

Use polish when you want to improve the quality of generated documentation templates. It transforms raw, auto-generated content into polished, readable help that follows documentation best practices.

## What's the main entry point?

Start with `polish_template()` — it takes your generated template content and returns an improved version. You'll also need `build_source_summary()` to create the source context that guides the polish pass.

## How does the polishing work?

The polish process uses template-specific system prompts that know how to improve different kinds of documentation (FAQs, reference pages, troubleshooting guides). The `get_system_prompt()` function provides the right instructions for each template type.

## What happens if polishing fails?

If you're running in strict mode, polish raises a `PolishError` when the LLM pass fails. You can control strict mode through the `STRICT_ENV_VAR` environment variable or the `strict` parameter.

## How do I debug polish issues?

Run `pytest -k "polish" -v` to check if the polish functionality is working correctly. If tests pass but you're still having issues, add debug logging at the failure point and check the LLM response for clues about what went wrong.

## Where are the source files?

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
