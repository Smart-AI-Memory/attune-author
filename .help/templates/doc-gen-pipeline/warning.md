---
type: warning
feature: doc-gen-pipeline
depth: warning
generated_at: 2026-04-11T05:00:50.763210+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline cautions

## What to watch for

The three-stage documentation generation pipeline (outline, write, review) uses LLM calls in sequence to improve output quality. Each stage depends on the previous one's output, creating opportunities for cascading failures and unexpected token consumption.

## Risk areas

### LLM token limits cause silent truncation

The pipeline doesn't validate that outline content fits within the `max_tokens` limit for subsequent stages. If `build_outline()` generates a large outline, `write_content()` may silently truncate the output when the combination of outline + source content exceeds the token budget.

**Mitigation:** Monitor token usage across stages and set conservative `max_tokens` values that account for the cumulative input size.

### Stage failures break the pipeline without recovery

Each pipeline stage (`build_outline`, `write_content`, `review_content`) makes blocking LLM calls. If any stage fails due to rate limits, network issues, or model errors, the entire `generate_docs()` operation fails with no partial output.

**Mitigation:** Implement retry logic with exponential backoff, or save intermediate stage outputs to allow manual recovery.

### Source content changes invalidate cached results

The pipeline doesn't detect when source files change between stages. If you modify the target file while documentation generation is running, later stages will work with stale outline or draft content that no longer matches the source.

**Mitigation:** Use file modification timestamps or content hashes to validate that source content remains consistent throughout the pipeline.

### Section focus filtering happens too late

The `section_focus` parameter in `write_content()` only affects content generation, not outline structure. If you want to focus on specific sections, an unfocused outline may still consume tokens describing sections you don't need.

**Mitigation:** Apply section filtering during the outline stage, or use targeted prompts that limit outline scope from the beginning.

## How to avoid problems

1. **Monitor token consumption patterns.** Track token usage across all three stages to identify when outline complexity pushes later stages toward truncation limits.

2. **Test with realistic source files.** Small test files may not reveal token budget issues that occur with production-sized codebases.

3. **Validate configuration before starting.** Check that `DocGenConfig` values make sense together — ensure `max_tokens` settings leave room for the cumulative input from previous stages.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
