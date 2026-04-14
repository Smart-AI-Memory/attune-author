---
type: faq
feature: doc-gen-pipeline
depth: faq
generated_at: 2026-04-14T16:19:14.014663+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline FAQ

## What is the doc gen pipeline?

A three-stage AI-powered documentation generator that creates high-quality docs by first outlining, then writing, then reviewing content.

## When should I use it?

Use the doc gen pipeline when you want AI to generate comprehensive documentation from your source code. It's particularly useful for API references, guides, and other technical documentation where you want structured, polished output rather than basic auto-generated docs.

## What's the main entry point?

Start with `generate_docs()` — it runs the full three-stage pipeline and returns a `DocGenResult` with your finished documentation. You can also call the individual stages (`build_outline()`, `write_content()`, `review_content()`) if you need more control over the process.

## How do I configure the pipeline?

Create a `DocGenConfig` object to control:
- Document type (defaults to 'api-reference')
- Target audience (defaults to 'developers')
- AI model (defaults to 'claude-sonnet-4-20250514')
- Token limits for each stage
- Which sections to focus on during writing

## What do I get back from generation?

A `DocGenResult` object containing:
- The final polished content
- The original outline
- The unreviewed draft
- List of completed stages
- Source file path

## Why might generation fail?

The most common issue is missing the Anthropic API dependency. If you get an `AnthropicCallError`, install the AI extras: `pip install 'attune-author[ai]'`.

## How do I debug pipeline issues?

Run `pytest -k "doc-gen-pipeline" -v` to check if the basic functionality works. For runtime issues, add debug logging at the stage where you suspect problems and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
