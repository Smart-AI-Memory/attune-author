---
type: concept
feature: rag-hook
depth: concept
generated_at: 2026-04-19T06:42:38.488219+00:00
source_hash: 65b7894e3d740f95f49a63218fbd54af3c2199aaf6aca5558be701274ef8f8e5
status: generated
---

# Rag Hook

The rag-hook feature enhances template polishing by retrieving real examples from existing attune-help documentation to guide LLM rewrites.

## How retrieval works

When you polish a generated template, the rag-hook can search through your existing attune-help documentation to find similar templates. This gives the LLM concrete examples to follow instead of making up patterns from scratch.

The hook retrieves the top 3 most relevant templates based on the feature name and template type. For example, when polishing a concept template about error handling, it might find other concept templates that document error-related features.

## Optional dependency design

The rag-hook implements graceful degradation so attune-author works whether or not you have the RAG capabilities installed:

- **Without `[rag]` extra**: The `rag_enabled()` function returns `False`, and polishing proceeds without retrieval
- **With `[rag]` extra**: The hook imports attune-rag and builds grounding context from your existing templates
- **Environment override**: Set `ATTUNE_AUTHOR_RAG` to disable RAG even when the dependencies are available

## Core functions

**`rag_enabled()`** checks whether RAG grounding should be active for the current polish operation. It returns `True` when the optional dependencies are available and not explicitly disabled.

**`ground_polish_context()`** searches your documentation and returns a formatted context block containing relevant template examples. The LLM receives this context along with the auto-generated template to improve its rewriting.
