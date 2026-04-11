---
type: faq
feature: polish
depth: faq
generated_at: 2026-04-11T04:49:08.223931+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Polish FAQ

## What is polish?

Polish improves auto-generated help templates by rewriting them with an LLM. It uses specialized prompts for different template types and includes source code context to ensure accuracy.

## When should I use polish?

Use polish when you have auto-generated templates that need improvement. The LLM rewrite makes them clearer, removes formulaic language, and follows documentation best practices while preserving technical accuracy.

## How do I polish a template?

Call `polish_template()` with your template content, feature name, source summary, and template type. The function returns the improved version.

## What template types does polish support?

Polish has specialized prompts for different template types like FAQ, reference, and concept pages. Use `get_system_prompt()` to see what types are available.

## How do I create a source summary?

Use `build_source_summary()` with your code's public classes, functions, docstrings, and file count. This summary helps the LLM understand what your code actually does.

## What happens if polishing fails?

In strict mode, polish raises a `PolishError` if the LLM can't improve the template. Otherwise, it returns the original content unchanged.

## How do I debug polish issues?

Run `pytest -k "polish" -v` first. If tests pass but your code fails, add debug logging at the failure point and check the LLM's response for errors.

## Where are the source files?

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
