---
type: troubleshooting
feature: rag-hook
depth: troubleshooting
generated_at: 2026-04-19T06:43:28.305701+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Troubleshoot rag hook

## Before you start

The RAG hook provides optional grounding for the attune-author polish pass. It retrieves related attune-help templates via attune-rag so the LLM rewriter can reference real patterns instead of inventing features. The module uses lazy imports and graceful degradation to keep attune-author installable without the `[rag]` extra.

## Symptom table

| If you observe | Check |
|----------------|-------|
| RAG grounding never activates | Run `python -c "from attune_author.rag_hook import rag_enabled; print(rag_enabled())"` to verify the function returns `True` |
| Polish pass gets empty context | Call `ground_polish_context()` directly with your feature name and template type to see if it returns `None` |
| Import errors on RAG functions | Verify the `[rag]` extra is installed: `pip show attune-author` should list attune-rag as a dependency |
| RAG disabled unexpectedly | Check if `ATTUNE_AUTHOR_RAG` environment variable is set (this disables RAG when present) |

## Step-by-step diagnosis

1. **Test RAG activation in isolation.**
   Verify the RAG hook responds correctly by running:
   ```bash
   python -c "from attune_author.rag_hook import rag_enabled; print(f'RAG enabled: {rag_enabled()}')"
   ```

2. **Check context generation.**
   Test the grounding function directly:
   ```python
   from attune_author.rag_hook import ground_polish_context
   result = ground_polish_context("your-feature", "troubleshooting", k=3)
   print(f"Context: {result}")
   ```

3. **Verify environment configuration.**
   Check if RAG is disabled via environment variable:
   ```bash
   echo $ATTUNE_AUTHOR_RAG
   ```
   If this prints anything, RAG is disabled.

4. **Test dependency availability.**
   Confirm attune-rag is accessible:
   ```python
   try:
       import attune_rag
       print("attune-rag available")
   except ImportError as e:
       print(f"attune-rag missing: {e}")
   ```

## Common fixes

- **Install the RAG extra.** If you get import errors, install with:
  ```bash
  pip install attune-author[rag]
  ```

- **Unset the disable flag.** If `ATTUNE_AUTHOR_RAG` is set, remove it:
  ```bash
  unset ATTUNE_AUTHOR_RAG
  ```

- **Check attune-rag configuration.** Empty context may indicate attune-rag can't find templates. Verify your attune-rag setup points to a valid template repository.

- **Increase retrieval count.** If context seems incomplete, try a higher `k` value in `ground_polish_context()` calls (default is 3).

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
