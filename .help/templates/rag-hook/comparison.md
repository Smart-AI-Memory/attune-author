---
type: comparison
feature: rag-hook
depth: comparison
generated_at: 2026-04-19T06:44:12.386720+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# RAG hook vs manual polish context

## Overview

The RAG hook provides optional retrieval-augmented generation for the polish pass. When enabled, it retrieves related attune-help templates through attune-rag, giving the LLM rewriter access to real patterns instead of forcing it to invent examples from scratch. The feature uses lazy imports and graceful degradation so attune-author remains installable without the `[rag]` extra.

## Feature comparison

| Aspect | RAG hook enabled | Manual polish only |
|--------|------------------|-------------------|
| **Context quality** | Grounded in existing templates | LLM relies on training data |
| **Dependencies** | Requires attune-rag extra | No additional deps |
| **Consistency** | References real project patterns | May invent non-existent features |
| **Performance** | Slower due to retrieval step | Fast, direct LLM calls |
| **Setup complexity** | Need vector store configured | Works immediately |
| **Reliability** | Degrades gracefully if RAG fails | Always available |

## Configuration control

You can disable RAG grounding by setting the `ATTUNE_AUTHOR_RAG` environment variable. The `rag_enabled()` function checks this setting and returns `True` by default, meaning RAG is enabled unless explicitly turned off.

The `ground_polish_context()` function retrieves the `k` most relevant templates (default 3) based on the feature name and template type being polished.

## Use RAG hook when

- You want polish output that references actual project patterns
- Consistency with existing help content matters more than speed
- You have the attune-rag dependency available
- You're polishing templates that benefit from seeing similar examples

## Use manual polish when

- You need the fastest possible polish times
- You're working in an environment without the RAG dependencies
- You're polishing content that doesn't benefit from template examples
- You're troubleshooting and want to isolate variables

## Recommendation

**Use RAG hook as the default.** The grounding significantly improves polish quality by preventing the LLM from inventing non-existent features or patterns. The performance cost is usually worth the accuracy gain, and the graceful degradation means you won't lose functionality if RAG is unavailable.

Only disable RAG when you specifically need faster iteration cycles during development or when working in constrained environments.

## Source files

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
