---
type: reference
feature: rag-hook
depth: reference
generated_at: 2026-04-26T19:50:59.992026+00:00
source_hash: d61374d79edea28930ef15ec35497f1fe3d5042dd35a449b02dca7cd837e332e
status: generated
---

# RAG grounding hook

Control RAG-enhanced polishing for the attune-author system.

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `rag_enabled()` | | `bool` | Return True when RAG grounding should be used |
| `ground_polish_context(feature_name, template_type, k=3)` | `feature_name: str, template_type: str, k: int = 3` | `str | None` | Build a grounding context block for the polish pass |

### ground_polish_context returns

The function returns a grounding context string containing:

```
True
```

## Constants

| Constant | Description |
|----------|-------------|
| `_DISABLE_ENV` | Environment variable name for disabling RAG: `'ATTUNE_AUTHOR_RAG'` |

## Source files

- `src/attune_author/rag_hook.py`

## Tags

`rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
