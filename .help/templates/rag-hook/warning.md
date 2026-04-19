---
type: warning
feature: rag-hook
depth: warning
generated_at: 2026-04-19T06:43:15.018802+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Rag Hook cautions

## What to watch for

The RAG hook provides optional grounding for the polish pass by retrieving related attune-help templates. While designed for graceful degradation, several runtime behaviors can cause unexpected failures or degraded output quality.

## Risk areas

### Environment variable conflicts

The `ATTUNE_AUTHOR_RAG` environment variable disables RAG grounding when set. This can cause confusion when the same codebase behaves differently across environments — templates that reference existing patterns in development may generate invented examples in production if the variable is accidentally set.

### Silent fallback to invention mode

When `ground_polish_context()` returns `None` (due to missing dependencies or RAG failures), the polish pass continues without grounding context. The LLM may then invent features, examples, or patterns that don't exist in your actual codebase. This degradation happens silently with no warning logs.

### Import dependency assumptions

The module uses lazy imports to avoid requiring the `[rag]` extra, but code that calls `ground_polish_context()` may assume RAG capabilities are available. If the extra isn't installed, you get `None` returns instead of the expected grounding context, leading to lower-quality polish output.

## How to avoid problems

1. **Verify RAG state explicitly.** Call `rag_enabled()` before relying on grounding context. Don't assume `ground_polish_context()` will return useful data.

2. **Monitor the `ATTUNE_AUTHOR_RAG` variable.** Check your deployment environments to ensure this variable isn't set unexpectedly. An unset variable enables RAG; any value disables it.

3. **Install the full dependency set.** If you want consistent RAG behavior, install with `pip install attune-author[rag]` rather than the base package alone.

4. **Test both RAG modes.** Run your polish workflows with RAG enabled and disabled to ensure acceptable output quality in both cases.

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
