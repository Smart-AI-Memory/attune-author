---
type: error
feature: doc-gen-pipeline
depth: error
generated_at: 2026-04-14T14:13:27.166301+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline errors

Documentation generation pipeline failures occur when the three-stage process (outline, write, review) encounters API limits, missing dependencies, or invalid source content.

## Common error signatures

- `AnthropicCallError` — Missing Anthropic API dependency or configuration
- Token limit exceeded errors during outline, write, or review stages
- JSON parsing failures when extracting outline sections
- File I/O errors when reading source files or writing output
- Configuration validation errors for invalid `doc_type` or `audience` values

## Where errors originate

The pipeline's three-stage architecture means failures can occur at different points:

- **`generate_docs()`** — Entry point that orchestrates the full pipeline and handles file I/O
- **`build_outline()`** — First stage that creates the document structure from source content
- **`write_content()`** — Second stage that generates draft content following the outline
- **`review_content()`** — Final stage that polishes the draft output
- **`parse_outline_sections()`** — Utility that extracts section headers for chunked writing

## How to diagnose

1. **Check for missing AI dependencies.** If you see `AnthropicCallError` with a pip install message, the pipeline requires the AI extras: `pip install 'attune-author[ai]'`

2. **Verify your source file exists and is readable.** The pipeline needs valid source content to analyze. Check that your target path is correct and the file contains parseable code or text.

3. **Review your `DocGenConfig` settings.** Token limits that are too low cause truncated output, while invalid `doc_type` or `audience` values may produce unexpected results.

4. **Monitor stage completion.** Check the `stages_completed` field in your `DocGenResult` to see which stage failed. An empty list means the outline stage failed; `['outline']` means writing failed; `['outline', 'write']` means review failed.

5. **Test with simpler content first.** If a large file fails, try generating docs for a smaller sample to isolate whether the issue is content complexity or configuration.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
