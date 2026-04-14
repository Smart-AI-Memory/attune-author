---
type: faq
feature: doc-gen-pipeline
depth: faq
generated_at: 2026-04-14T14:14:15.010423+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline FAQ

## What is the doc gen pipeline?

A three-stage documentation generation system that uses AI to create higher-quality docs through structured planning: first building an outline, then writing content, and finally reviewing and polishing the result.

## When should I use the doc gen pipeline?

Use it when you want AI-generated documentation that's more structured and thoughtful than single-pass generation. The multi-stage approach produces better organization and content quality, especially for complex API references or detailed guides.

## What's the main entry point?

Start with `generate_docs()` — it runs the complete three-stage pipeline and returns a `DocGenResult` with the final content plus intermediate outputs from each stage.

For more control, you can call the individual stage functions:
- `build_outline()` — Creates the documentation structure
- `write_content()` — Fills in the content from the outline
- `review_content()` — Polishes the draft

## How do I configure the pipeline?

Create a `DocGenConfig` object to control the generation process:

```python
config = DocGenConfig(
    doc_type='user-guide',  # or 'api-reference'
    audience='end-users',   # or 'developers'
    model='claude-sonnet-4-20250514',
    max_write_tokens=8000
)
```

You can also pass configuration directly to `generate_docs()` or use the defaults.

## What do I get back from generate_docs()?

A `DocGenResult` object containing:
- `content` — The final polished documentation
- `outline` — The structure created in stage 1
- `draft` — The unpolished content from stage 2
- `stages_completed` — Which pipeline stages finished successfully
- `source_path` — Path to the source file that was processed

## How do I debug pipeline failures?

Run `pytest -k "doc-gen-pipeline" -v` first to check if the issue is environmental.

If tests pass but your generation fails, check the `stages_completed` field in your `DocGenResult` to see where the pipeline stopped. The pipeline saves intermediate outputs, so you can inspect the `outline` or `draft` fields to debug content issues.

## Do I need special dependencies?

Yes, you need the AI extras: `pip install 'attune-author[ai]'`

The pipeline will raise an `AnthropicCallError` with installation instructions if the dependencies are missing.

## Where are the source files?

- `src/attune_author/doc_gen/pipeline.py` — Main orchestration
- `src/attune_author/doc_gen/stages.py` — Individual stage implementations
- `src/attune_author/doc_gen/config.py` — Configuration classes

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
