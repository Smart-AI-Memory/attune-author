---
type: warning
feature: polish
depth: warning
generated_at: 2026-04-11T04:48:41.260957+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243dcf298bae31fb8dc0
status: generated
---

# Polish cautions

## What to watch for

The polish feature rewrites generated documentation using LLM calls, which can fail unpredictably or produce inconsistent output when source information is incomplete.

## Risk areas

**LLM failures in strict mode**
When `polish_template()` runs with `strict=True` (the default), API failures or malformed responses raise `PolishError` instead of returning the original content. This can break automated workflows that expect polish to always succeed.

**Incomplete source summaries**
`build_source_summary()` constructs the context that guides the polish pass. If you pass empty or minimal data (missing docstrings, incomplete function signatures), the LLM may hallucinate features or produce generic advice that doesn't match your actual code.

**Template type mismatches**
`get_system_prompt()` returns different instructions for each template type (warning, guide, reference, etc.). Using the wrong type can result in content that follows the wrong format or answers the wrong questions for your documentation needs.

## How to avoid problems

1. **Handle polish failures gracefully.** Set `strict=False` when polish is optional, or catch `PolishError` and fall back to the original template:
   ```python
   try:
       polished = polish_template(content, "myfeature", summary, strict=True)
   except PolishError:
       polished = content  # Use original on failure
   ```

2. **Verify source summaries before polishing.** Check that `build_source_summary()` includes meaningful docstrings and function signatures. Empty summaries lead to generic, unhelpful output.

3. **Match template types to content.** Ensure the `template_type` parameter matches what you're actually generating. A reference template polished as a guide will have the wrong structure and tone.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
