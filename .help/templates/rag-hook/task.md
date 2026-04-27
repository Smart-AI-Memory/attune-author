---
type: task
feature: rag-hook
depth: task
generated_at: 2026-04-26T19:50:48.254347+00:00
source_hash: d61374d79edea28930ef15ec35497f1fe3d5042dd35a449b02dca7cd837e332e
status: generated
---

# Work with rag hook

Use rag hook when you need to add contextual grounding to the template polish pass or modify how attune-author retrieves related help content.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/rag_hook.py`

## Check if RAG is enabled

1. **Call the detection function.**
   Use `rag_enabled()` to check whether RAG grounding is available:
   ```python
   from attune_author.rag_hook import rag_enabled

   if rag_enabled():
       # RAG is available
   else:
       # Fall back to non-RAG behavior
   ```

2. **Handle the disabled state.**
   When RAG is disabled (via `ATTUNE_AUTHOR_RAG` environment variable), your code should degrade gracefully without the extra context.

## Retrieve grounding context

1. **Build the context block.**
   Call `ground_polish_context()` with your feature name and template type:
   ```python
   from attune_author.rag_hook import ground_polish_context

   context = ground_polish_context("your-feature", "task", k=3)
   ```

2. **Handle the None case.**
   The function returns `None` when RAG is disabled or no relevant templates are found:
   ```python
   if context:
       # Include context in your polish prompt
       prompt = f"Context:\n{context}\n\nTemplate to polish:\n{template}"
   else:
       # Polish without additional context
       prompt = f"Template to polish:\n{template}"
   ```

## Modify RAG behavior

1. **Locate the function you need.**
   - `rag_enabled()` controls when RAG grounding runs
   - `ground_polish_context()` builds the context block from retrieved templates

2. **Follow the existing patterns.**
   - Use lazy imports to keep dependencies optional
   - Return graceful defaults when RAG is unavailable
   - Maintain the same return types and error handling

3. **Test your changes.**
   Run the test suite to verify your modifications work:
   ```bash
   pytest -k "rag_hook"
   ```

## Verification

You successfully modified the rag hook when:
- `rag_enabled()` returns the expected boolean value
- `ground_polish_context()` returns properly formatted context or `None` as appropriate
- The system gracefully handles cases when RAG dependencies are unavailable
- All existing tests pass
