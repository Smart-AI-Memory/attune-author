---
type: task
feature: rag-hook
depth: task
generated_at: 2026-04-19T06:42:48.889284+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Work with rag hook

Use the RAG hook when you need to enhance LLM template polishing with real examples from existing documentation instead of letting the model invent patterns.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/rag_hook.py`

## Enable RAG grounding

1. **Check if RAG is available.**
   Call `rag_enabled()` to verify the RAG system is installed and not disabled via the `ATTUNE_AUTHOR_RAG` environment variable.

2. **Retrieve grounding context.**
   Call `ground_polish_context(feature_name, template_type, k=3)` to get relevant examples:
   - `feature_name`: The feature you're documenting
   - `template_type`: The type of template being polished
   - `k`: Number of related examples to retrieve (default: 3)

3. **Verify context retrieval.**
   The function returns a string with grounding context when successful, or `None` when RAG is unavailable or no relevant examples exist.

## Configure RAG behavior

1. **Disable RAG when needed.**
   Set the `ATTUNE_AUTHOR_RAG` environment variable to disable RAG grounding entirely.

2. **Adjust retrieval count.**
   Pass a different `k` value to `ground_polish_context()` to control how many examples are retrieved for grounding.

## Test your changes

Run the RAG hook tests to verify your modifications work correctly:

```bash
pytest -k "rag-hook"
```

## Verify success

Your RAG hook integration works when:
- `rag_enabled()` returns `True` when the RAG system is available
- `ground_polish_context()` returns relevant example content for valid feature names
- The system gracefully handles missing RAG dependencies without breaking attune-author

## Key files

- `src/attune_author/rag_hook.py`
