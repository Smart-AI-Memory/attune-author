---
type: note
feature: rag-hook
depth: note
generated_at: 2026-04-19T06:44:06.544021+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Note: rag hook

## Context

The rag hook provides optional RAG (Retrieval-Augmented Generation) grounding for attune-author's polish pass. When enabled, it retrieves related attune-help templates via attune-rag so the LLM can reference real documentation patterns instead of inventing them.

The implementation uses lazy imports and graceful degradation, which keeps attune-author installable without the optional `[rag]` extra.

## How it works

The rag hook exposes two main functions:

- `rag_enabled()` — Returns `True` when RAG grounding should be used
- `ground_polish_context()` — Builds a grounding context block for the polish pass by retrieving the top k most relevant templates

You can disable RAG grounding by setting the `ATTUNE_AUTHOR_RAG` environment variable, regardless of whether the rag dependencies are installed.

The module handles missing dependencies gracefully — if attune-rag isn't available, `rag_enabled()` returns `False` and the polish pass continues without grounding context.

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
