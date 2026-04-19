---
type: reference
feature: rag-hook
depth: reference
generated_at: 2026-04-19T06:42:59.651278+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# RAG hook reference

Check whether RAG grounding is enabled and build retrieval-augmented context for polish passes.

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `rag_enabled()` | | `bool` | Return True when RAG grounding should be used |
| `ground_polish_context()` | `feature_name: str, template_type: str, k: int = 3` | `str \| None` | Build a grounding context block for the polish pass |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_DISABLE_ENV` | `'ATTUNE_AUTHOR_RAG'` | Environment variable name to disable RAG grounding |

## Source files

- `src/attune_author/rag_hook.py`

## Tags

`rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
