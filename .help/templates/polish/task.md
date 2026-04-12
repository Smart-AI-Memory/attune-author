---
type: task
feature: polish
depth: task
generated_at: 2026-04-12T04:18:28.601212+00:00
source_hash: 9f00fa4d4bf451430bdb559d13e2781477df4a00e9c10586bff49eaa38404dbc
status: generated
---

# Work with polish

Use polish when you need to enhance auto-generated help templates by applying LLM-based refinements with template-specific prompts and source code context.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/polish.py` and `src/attune_author/polish_prompts.py`

## Steps

1. **Identify the polish component to modify**

   Examine these three core functions to determine which handles your use case:
   - `polish_template()` — Sends templates to the LLM with context and prompts
   - `build_source_summary()` — Creates source code summaries for LLM context
   - `get_system_prompt()` — Retrieves template-type-specific system prompts

2. **Review the target function's implementation**

   Read the function's docstring, parameters, and return type. Check how it handles the `PolishError` exception and any strict mode requirements.

3. **Implement your changes**

   Modify the function while maintaining the existing parameter signatures and error handling patterns. Ensure strict mode behavior remains consistent.

4. **Test the polish functionality**

   Run `pytest -k "polish"` to verify your changes work correctly and don't break existing functionality.

## Key files

- `src/attune_author/polish.py` — Core polish functions
- `src/attune_author/polish_prompts.py` — Template-specific system prompts

## Success criteria

Your changes work when:
- The polish tests pass without errors
- Templates are refined according to your modifications
- `PolishError` is raised appropriately in strict mode when polish fails
