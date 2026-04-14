---
type: warning
feature: polish
depth: warning
generated_at: 2026-04-14T16:04:55.829496+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Polish cautions

## What to watch for

The `polish` module uses LLM API calls to rewrite auto-generated templates. Since it makes external network requests and processes untrusted content, several failure modes can cause delays or incorrect output in your documentation pipeline.

## Risk areas

- **API failures cascade into build failures** — `polish_template()` calls Anthropic's API, which can timeout, rate-limit, or return malformed responses. In strict mode, any API failure raises `PolishError` and stops your build.

- **LLM hallucinations corrupt technical accuracy** — The polish pass can introduce incorrect function names, non-existent parameters, or wrong behavior descriptions. The system prompts try to prevent this, but LLMs sometimes ignore grounding constraints.

- **Environment variable confusion in strict mode** — The `STRICT_ENV_VAR` constant controls error handling, but its falsy values (`'0'`, `'false'`, `'no'`, `'off'`) are case-sensitive strings, not booleans. Setting `ATTUNE_AUTHOR_STRICT_POLISH=False` (with capital F) enables strict mode when you expect it disabled.

- **Source summary truncation loses context** — `build_source_summary()` condenses your codebase info for the LLM prompt. For large modules, important details about parameter validation or edge cases may get compressed out, leading to incomplete warnings in polished templates.

## How to avoid problems

1. **Handle API failures gracefully** — Set strict mode to `False` in production builds unless you can tolerate documentation generation failures. Use `try/except PolishError` around `polish_template()` calls when you need custom error handling.

2. **Validate polished output** — After polishing, scan the result for function names and behavior claims that don't match your source code. The polish pass sometimes merges information from different functions or invents plausible-sounding but wrong details.

3. **Test with realistic source summaries** — Use `build_source_summary()` with representative data from your actual modules, not toy examples. Large function lists or complex inheritance hierarchies can trigger summary truncation that affects polish quality.

4. **Check environment variable spelling** — Verify that `ATTUNE_AUTHOR_STRICT_POLISH` is exactly one of the recognized falsy values if you want non-strict mode. Typos or unexpected capitalization will enable strict mode by default.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
