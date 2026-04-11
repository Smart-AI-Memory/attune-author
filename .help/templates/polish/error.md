---
type: error
feature: polish
depth: error
generated_at: 2026-04-11T04:48:29.016890+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Polish errors

Failures during LLM-powered template refinement, including API connectivity issues, prompt formatting problems, and strict mode validation failures.

## Common error signatures

- `PolishError` — Raised when the polish pass fails in strict mode, typically after multiple retry attempts or when the LLM output doesn't meet quality thresholds
- `requests.exceptions.RequestException` — Network connectivity issues when calling the LLM API during `polish_template()`
- `KeyError` — Missing template type when `get_system_prompt()` receives an unrecognized template kind
- `json.JSONDecodeError` — Malformed API response from the LLM service

## Where errors originate

Polish errors typically originate from three main functions:

- `polish_template()` — Orchestrates the LLM call and handles retries. Raises `PolishError` when strict mode is enabled and the polish pass fails after exhausting retry attempts.
- `build_source_summary()` — Constructs the source context for the LLM prompt. Can raise exceptions if the input data structures are malformed or missing required fields.
- `get_system_prompt()` — Retrieves template-specific prompts. Raises `KeyError` when the template type isn't recognized in the prompt mapping.

## How to diagnose

1. **Check if strict mode is enabled.** `PolishError` only appears when `strict=True` is passed to `polish_template()`. If you're seeing these exceptions, the LLM output failed validation multiple times.

2. **Verify API connectivity.** Network-related failures during the LLM call manifest as connection timeouts or HTTP errors. Test your API endpoint and credentials separately.

3. **Validate the template type.** If `get_system_prompt()` raises a `KeyError`, check that you're passing a supported template type ('error', 'feature', etc.) to `polish_template()`.

4. **Inspect the source summary structure.** `build_source_summary()` expects specific dictionary structures for classes and functions. Verify that your input data matches the expected format with required string keys.

## Source files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

**Tags:** `polish`, `llm`, `anthropic`, `quality`
