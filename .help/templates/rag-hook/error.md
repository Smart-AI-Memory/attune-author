---
type: error
feature: rag-hook
depth: error
generated_at: 2026-04-19T06:43:03.899896+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Rag Hook errors

RAG hook failures occur when the optional retrieval-augmented grounding system encounters import problems, configuration issues, or retrieval errors during the polish pass.

## Common error signatures

- `ModuleNotFoundError: No module named 'attune_rag'` — The `[rag]` extra is not installed
- `ImportError` during lazy import of RAG dependencies
- `ValueError` from invalid `k` parameter in `ground_polish_context()`
- Retrieval timeouts or connection errors from the underlying RAG system

## Where errors originate

RAG hook errors stem from two main functions:

- `rag_enabled()` — Checks environment variables and import availability to determine if RAG should be active
- `ground_polish_context()` — Retrieves related templates and builds grounding context, handling all RAG system interactions

Since this module uses graceful degradation, import failures in `rag_enabled()` are caught and return `False` rather than propagating. However, if `ground_polish_context()` is called when RAG is unavailable, exceptions will propagate to the polish pass.

## How to diagnose

1. **Check if the RAG extra is installed.** Run `pip show attune-author` and verify the `[rag]` extra appears in the installation. If not, reinstall with `pip install attune-author[rag]`.

2. **Verify the environment variable.** The `ATTUNE_AUTHOR_RAG` environment variable disables RAG when set. Check if this variable exists and unset it if RAG should be enabled.

3. **Test RAG availability separately.** Call `rag_enabled()` directly to confirm the system can import and initialize RAG dependencies without errors.

4. **Validate the retrieval parameters.** If `ground_polish_context()` fails, check that `feature_name` and `template_type` are valid strings and `k` is a positive integer.

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
