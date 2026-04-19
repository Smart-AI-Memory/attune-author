---
type: tip
feature: rag-hook
depth: tip
generated_at: 2026-04-19T06:44:00.371241+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Tip: working effectively with rag hook

## Context

Optional RAG grounding for the polish pass — retrieves related attune-help templates via attune-rag so the LLM rewrite references real patterns instead of inventing them. Lazy imports and graceful degradation keep attune-author installable without the [rag] extra.

## Recommendation

Always check `rag_enabled()` before calling `ground_polish_context()`. The RAG hook degrades gracefully when the optional dependencies are missing, but only if you check availability first.

## Why this matters

Calling `ground_polish_context()` without checking `rag_enabled()` can fail silently or throw import errors depending on your environment, making debugging harder than it needs to be.

## Tradeoff

The extra function call adds one line to your code, but it makes the RAG integration much more predictable across different installation configurations.

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
