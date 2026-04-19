---
type: faq
feature: rag-hook
depth: faq
generated_at: 2026-04-19T06:43:41.469617+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Rag Hook FAQ

## What is rag hook?

The rag hook provides optional RAG (Retrieval-Augmented Generation) grounding for the polish pass. It retrieves related attune-help templates via attune-rag so the LLM can reference real patterns instead of inventing features. The module uses lazy imports and graceful degradation, so attune-author works even without the [rag] extra installed.

## When should I use it?

You should use the rag hook when you want the polish pass to reference existing documentation patterns from your project. This improves the quality of generated help by grounding rewrites in actual examples rather than hallucinated content.

## How do I check if RAG is enabled?

Call `rag_enabled()`. It returns `True` when RAG grounding should be used.

## How do I get grounding context for polishing?

Use `ground_polish_context(feature_name, template_type, k=3)`. This builds a context block containing relevant templates for the polish pass. The `k` parameter controls how many related templates to retrieve.

## How do I disable RAG grounding?

Set the `ATTUNE_AUTHOR_RAG` environment variable. When this variable is present, RAG grounding is disabled.

## How do I debug it?

Run the related tests first: `pytest -k "rag-hook" -v`. If they pass but your code still fails, add a `logger.debug` statement at the suspected failure point and re-run with logging enabled.

For common failure modes, see the troubleshooting page for this feature.

## Where are the source files?

- `src/attune_author/rag_hook.py`

**Tags:** `rag`, `retrieval`, `grounding`, `polish`, `optional-extra`
