---
type: task
feature: doc-gen-pipeline
depth: task
generated_at: 2026-04-14T16:18:05.012602+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Work with doc gen pipeline

Use the doc gen pipeline when you need to generate high-quality documentation through a structured three-stage process: outline creation, content writing, and review.

## Prerequisites

- Access to the project source code
- Anthropic API key (install with `pip install 'attune-author[ai]'`)
- Basic understanding of the pipeline stages

## Configure the pipeline

1. **Set up your configuration.**
   Create a `DocGenConfig` instance to specify your documentation requirements:
   ```python
   from attune_author.doc_gen.pipeline import DocGenConfig

   config = DocGenConfig(
       doc_type='api-reference',  # or 'tutorial', 'guide', etc.
       audience='developers',
       model='claude-sonnet-4-20250514',
       max_outline_tokens=1000,
       section_focus=['usage examples', 'error handling']
   )
   ```

2. **Identify your source target.**
   Specify the file path or content you want to document:
   - For a source file: use the file path as the `target` parameter
   - For raw content: pass the content string directly

## Generate documentation

1. **Run the pipeline.**
   Call `generate_docs()` with your target and configuration:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs

   result = generate_docs(
       target='src/my_module.py',
       config=config,
       output_path='docs/my_module.md'
   )
   ```

2. **Access the results.**
   The `DocGenResult` contains all pipeline outputs:
   ```python
   print(f"Generated outline: {result.outline}")
   print(f"Final content: {result.content}")
   print(f"Stages completed: {result.stages_completed}")
   ```

## Verify success

The pipeline completed successfully when:
- `result.stages_completed` includes `['outline', 'write', 'review']`
- `result.content` contains the final polished documentation
- If you specified an `output_path`, the file was created at that location

## Key files

- `src/attune_author/doc_gen/pipeline.py` — Main orchestrator and `generate_docs()` function
- `src/attune_author/doc_gen/stages.py` — Individual stage implementations
- `src/attune_author/doc_gen/config.py` — Configuration dataclasses

## Customize individual stages

For advanced use cases, call the stage functions directly:

- **`build_outline()`** — Generate a structured outline from source content
- **`write_content()`** — Convert an outline into documentation draft
- **`review_content()`** — Polish and refine the draft content
- **`parse_outline_sections()`** — Extract section titles from generated outlines
