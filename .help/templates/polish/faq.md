---
type: faq
feature: polish
depth: faq
generated_at: 2026-04-14T16:05:26.899393+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish FAQ

## What is polish?

A feature that improves auto-generated help templates by running them through an LLM with specialized prompts for different template types.

## When should I use polish?

Use polish when you want to improve the quality of generated documentation templates. It takes raw auto-generated content and rewrites it to be more readable and follow documentation best practices.

## What's the main entry point?

Start with `polish_template()` — it takes your generated template content and returns a polished version. You'll need to provide the feature name, source summary, and template type.

For building the source summary that polish needs, use `build_source_summary()`.

## How does polish work?

Polish uses different system prompts for different template types (FAQ, reference, etc.). You can see what prompt will be used for a given template type by calling `get_system_prompt()`.

## What happens if polish fails?

By default, polish returns the original content if the LLM call fails. In strict mode, it raises a `PolishError` instead. You can control strict mode with the `strict` parameter or the `ATTUNE_AUTHOR_STRICT_POLISH` environment variable.

## How do I debug polish issues?

Run `pytest -k "polish" -v` first to check if the basic functionality works. If polish is failing on your specific content, check the error message for details about what went wrong during the LLM call.

## Where are the source files?

- `src/attune_author/polish.py` — Main polish functionality
- `src/attune_author/polish_prompts.py` — Template-specific system prompts

**Tags:** `polish`, `llm`, `anthropic`, `quality`
