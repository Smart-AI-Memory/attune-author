---
type: warning
feature: polish
depth: warning
generated_at: 2026-04-14T14:00:02.214737+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Polish cautions

## What to watch for

The polish feature uses LLM calls to rewrite generated templates, which introduces several failure modes that can break your documentation build or produce incorrect output.

## Risk areas

### LLM API failures break the build in strict mode

When `polish_template()` runs with `strict=True` (the default in CI environments), any Anthropic API error raises `PolishError` and stops your build. Network timeouts, rate limits, and invalid API keys all trigger this behavior.

**Mitigation:** Set `ATTUNE_AUTHOR_STRICT_POLISH=false` in environments where you prefer degraded output over build failures. The function will return the unpolished template instead of raising an exception.

### Template type mismatches produce irrelevant output

The `get_system_prompt()` function returns different prompts for 'reference', 'tutorial', 'warning', and other template types. If you pass the wrong `template_type` to `polish_template()`, the LLM will follow inappropriate instructions—for example, trying to add code examples to a warning page.

**Mitigation:** Ensure your `template_type` parameter matches the actual template structure. The type should align with the template's intended purpose, not its file extension or location.

### Source summaries can exceed LLM context limits

The `build_source_summary()` function concatenates module docstrings, function signatures, and class definitions. For large codebases, this summary may exceed the LLM's context window, causing truncated or failed requests.

**Mitigation:** Monitor the length of generated summaries, especially when documenting modules with many public functions. Consider filtering or summarizing the input data before passing it to `build_source_summary()`.

## How to avoid problems

1. **Test API connectivity early.** Run `polish_template()` with a minimal example before integrating it into your build pipeline. Verify that your Anthropic API key works and has sufficient quota.

2. **Match template types precisely.** Double-check that your `template_type` parameter corresponds to the content structure. A mismatch will waste API calls and produce confusing documentation.

3. **Monitor context length.** For modules with more than 20-30 public functions, check the output of `build_source_summary()` before sending it to the LLM. Large summaries may need manual curation.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
