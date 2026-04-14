---
type: warning
feature: doc-gen-pipeline
depth: warning
generated_at: 2026-04-14T14:13:41.572398+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline cautions

## What to watch for

The doc-gen-pipeline uses a three-stage AI workflow (outline, write, review) that can fail at any stage or produce unexpected output when token limits are exceeded or AI models are unavailable.

## Risk areas

**Token budget exhaustion in multi-stage processing**

Each stage (`build_outline`, `write_content`, `review_content`) has separate token limits that default to 1000, 8000, and 8000 respectively. Large source files can exceed these limits, causing truncated outlines that lead to incomplete documentation in subsequent stages.

**AI model dependency without graceful degradation**

The pipeline requires an active Anthropic API connection and raises `AnthropicCallError` if the AI service is unavailable. The error message suggests installing the `ai` extra, but network issues, quota limits, or API downtime will also trigger failures with no local fallback.

**Section focus filtering in content generation**

The `section_focus` parameter in `DocGenConfig` filters which outline sections get detailed content. If you specify sections that don't exist in the generated outline, `write_content` will produce sparse documentation without warning about the mismatch.

**Outline parsing assumptions in chunked processing**

The `parse_outline_sections` function expects specific markdown heading formats. If the AI generates outlines in unexpected formats (nested lists, numbered sections, or non-standard heading syntax), the section parser may miss content boundaries, leading to incorrectly chunked writing stages.

## How to avoid problems

**Monitor token usage across stages.** Check that your source content fits within the configured token limits. For large files, increase `max_outline_tokens`, `max_write_tokens`, and `max_review_tokens` in your `DocGenConfig`, or break content into smaller chunks.

**Handle AI service failures.** Wrap `generate_docs()` calls in try-except blocks to catch `AnthropicCallError`. Consider implementing retry logic with exponential backoff for transient network issues.

**Validate section focus against generated outlines.** After calling `build_outline()`, use `parse_outline_sections()` to verify that your `section_focus` list matches actual section titles before proceeding to `write_content()`.

**Test with diverse source formats.** The outline parser works best with standard Python modules. Test your pipeline with edge cases like empty files, unusual docstring formats, or heavily nested code structures.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
