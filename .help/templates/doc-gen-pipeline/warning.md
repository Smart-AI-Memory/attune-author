---
type: warning
feature: doc-gen-pipeline
depth: warning
generated_at: 2026-04-14T16:18:41.171877+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline cautions

## What to watch for

The doc-gen-pipeline orchestrates three-stage LLM-based documentation generation (outline, write, review) for higher-quality help output. Token limits, incomplete stage execution, and missing Anthropic API credentials can disrupt the pipeline and produce partial results.

## Risk areas

### Token limit overruns in content generation

The `write_content()` stage defaults to 8,000 tokens, which may be insufficient for complex source files. When the limit is hit mid-generation, you get truncated documentation with incomplete sections or cut-off sentences. The `max_write_tokens` parameter in `DocGenConfig` controls this limit, but there's no automatic fallback when exceeded.

### Partial pipeline execution with incomplete results

If any stage fails, `generate_docs()` returns a `DocGenResult` with only the `stages_completed` field populated up to the failure point. For example, if outline generation succeeds but writing fails, you'll have an outline but empty `content` and `draft` fields. Always check `stages_completed` before using other result fields.

### Missing Anthropic API installation

The pipeline requires the optional `ai` extras package. Without it, `generate_docs()` raises `AnthropicCallError` with installation instructions. This happens at runtime, not import time, so tests may pass until you actually call the generation functions.

### Section focus filtering creates gaps

When you specify `section_focus` in `DocGenConfig`, the `write_content()` stage only generates those sections. If your focus list doesn't match the actual outline sections from `build_outline()`, you'll get empty or partial content. Use `parse_outline_sections()` to verify section names before filtering.

## How to avoid problems

1. **Set realistic token limits.** Check your source file size and adjust `max_write_tokens` accordingly. Large API references may need 12,000+ tokens for complete coverage.

2. **Check stages_completed before using results.** Always verify that all three stages completed before depending on the final content:
   ```python
   result = generate_docs(target, config)
   if len(result.stages_completed) != 3:
       # Handle partial generation
   ```

3. **Install with AI extras for production.** Include `pip install 'attune-author[ai]'` in your deployment to avoid runtime API errors.

4. **Test section focus against real outlines.** Run `build_outline()` first to see actual section names, then configure `section_focus` to match.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
