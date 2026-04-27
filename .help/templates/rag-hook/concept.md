---
type: concept
feature: rag-hook
depth: concept
generated_at: 2026-04-26T19:50:37.332949+00:00
source_hash: d61374d79edea28930ef15ec35497f1fe3d5042dd35a449b02dca7cd837e332e
status: generated
---

# RAG Hook

The RAG hook provides optional retrieval-augmented generation for template polishing, letting the AI rewriter reference real attune-help patterns instead of inventing content.

## Core responsibilities

The hook acts as a bridge between attune-author's polish pass and the attune-rag system. When enabled, it retrieves existing templates that match the feature being polished, giving the LLM concrete examples of style, structure, and naming conventions to follow.

Two functions handle this integration:

- **`rag_enabled()`** checks whether RAG grounding is available and should be used
- **`ground_polish_context()`** fetches related templates and formats them as context for the polish prompt

## Graceful degradation model

The hook uses lazy imports and optional dependencies to keep attune-author lightweight. If the `[rag]` extra isn't installed or the `ATTUNE_AUTHOR_RAG` environment variable is set, RAG grounding is silently disabled and polishing continues without retrieval context.

This design lets users install attune-author standalone for basic template generation while providing enhanced polish quality when the full RAG stack is available.

## Integration with the polish workflow

During template polishing, the hook retrieves up to 3 related templates based on feature name and template type. These examples appear in the LLM prompt as "Related existing templates (for reference)" — giving the AI concrete patterns to follow rather than generating formulaic placeholder content.

The retrieved templates serve as style guides, showing real section structures, naming conventions, and content depth that match the project's documentation standards.
