---
type: task
feature: polish
depth: task
generated_at: 2026-04-26T19:47:10.811578+00:00
source_hash: c3c5a14decb406edb1b2d8ca09a6adb5d3bf68908f60cdaf9a9ea6ba0df1471d
status: generated
---

# Work with polish

Use the polish module when you need to improve auto-generated template quality through LLM rewriting that applies type-specific style rules and source-grounded accuracy checks.

## Prerequisites

- Access to the project source code
- Understanding of template types and their style conventions
- Familiarity with the polish module structure

## Steps

1. **Identify the polish function you need to modify.**
   The module separates concerns into three main functions:
   - `polish_template()` — Orchestrates the LLM rewriting process
   - `build_source_summary()` — Creates concise source descriptions for prompt context
   - `get_system_prompt()` — Retrieves type-specific style rules

2. **Review the function's current implementation.**
   Read the docstring, parameter types, and return values to understand the function's scope and constraints.

3. **Implement your changes following the module patterns.**
   Maintain the existing error handling style, use the `PolishError` for polish failures, and preserve the source-grounded accuracy approach.

4. **Test your changes with the polish test suite.**
   Run `pytest -k "polish"` to verify your modifications don't break existing functionality.

## Verify success

Your changes work correctly when:
- The polish test suite passes without errors
- Generated templates maintain their factual accuracy while improving in readability
- Type-specific style rules are properly applied based on the template kind

## Key files

- `src/attune_author/polish.py` — Core polish functions
- `src/attune_author/polish_prompts.py` — Type-specific system prompts
