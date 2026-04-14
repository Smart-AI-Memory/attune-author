---
type: comparison
feature: polish
depth: comparison
generated_at: 2026-04-14T16:05:59.756580+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish vs manual editing

## Overview

The `polish` feature uses an LLM to automatically improve generated help templates, applying type-specific system prompts and source-grounded summaries. Compare this to manually editing templates or using generic text improvement tools.

## Feature comparison

| Aspect | Polish feature | Manual editing | Generic AI tools |
|--------|---------------|----------------|------------------|
| **Speed** | Processes templates in seconds | Requires writer time per template | Fast but needs context setup |
| **Consistency** | Template-type-aware prompts ensure uniform structure | Varies by editor skill/attention | No template structure awareness |
| **Source accuracy** | Grounded in actual code via `build_source_summary()` | Relies on editor's code knowledge | Risk of hallucinated features |
| **Scale** | Handles batch processing efficiently | Doesn't scale to many templates | Manual prompt engineering per use |
| **Customization** | Fixed prompts per template type | Unlimited flexibility | Requires custom prompt development |
| **Error handling** | Raises `PolishError` in strict mode | No automated validation | No built-in validation |

## When to use polish

Choose the polish feature when:

- **You generate multiple templates** — The type-specific prompts (`get_system_prompt()`) handle comparison, reference, and tutorial formats automatically
- **Source accuracy matters** — The `build_source_summary()` function ensures the LLM works from actual code signatures and docstrings
- **You want consistent quality** — The same prompts produce uniform output across template batches
- **You're in a CI/CD pipeline** — Set `strict=True` to fail builds when polish can't improve a template

## When manual editing works better

Prefer manual editing when:

- **You need deep customization** — The polish prompts target general improvements, not domain-specific restructuring
- **Working with one-off templates** — Manual editing is faster than setting up polish for single uses
- **Templates need creative restructuring** — Polish improves existing structure but won't completely reimagine organization

## Decision rule

Use polish by default for generated templates. The `polish_template()` function with source-grounded prompts produces better results than manual editing for most technical documentation. Fall back to manual work only when you need structural changes that go beyond the template type's standard format.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
