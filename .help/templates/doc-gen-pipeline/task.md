---
type: task
feature: doc-gen-pipeline
depth: task
generated_at: 2026-04-12T04:21:04.043752+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Work with doc gen pipeline

Use the doc gen pipeline when you need to generate high-quality documentation through a structured three-stage process that creates an outline, writes content, and reviews the output.

## Prerequisites

- Access to the project source code
- Anthropic API client configured
- Understanding of the target documentation type and audience

## Generate documentation

1. **Import the pipeline module:**
   ```python
   from attune_author.doc_gen.pipeline import generate_docs, DocGenConfig
   ```

2. **Create a configuration (optional):**
   ```python
   config = DocGenConfig(
       doc_type="tutorial",
       audience="beginner",
       model="claude-3-sonnet-20241022"
   )
   ```

3. **Run the documentation generation:**
   ```python
   result = generate_docs(
       target="path/to/source.py",
       config=config,
       output_path="docs/output.md"
   )
   ```

4. **Verify the output:**
   Check that the `DocGenResult` contains your generated documentation and that the output file exists at the specified path.

## Customize individual stages

1. **Set up the Anthropic client:**
   ```python
   from anthropic import Anthropic
   client = Anthropic()
   ```

2. **Generate an outline first:**
   ```python
   from attune_author.doc_gen.stages import build_outline

   outline = build_outline(
       client=client,
       source_content=source_text,
       doc_type="guide",
       audience="intermediate",
       model="claude-3-sonnet-20241022",
       max_tokens=2000
   )
   ```

3. **Write content from the outline:**
   ```python
   from attune_author.doc_gen.stages import write_content

   draft = write_content(
       client=client,
       outline=outline,
       source_content=source_text,
       doc_type="guide",
       audience="intermediate",
       model="claude-3-sonnet-20241022",
       max_tokens=4000
   )
   ```

4. **Review and polish the draft:**
   ```python
   from attune_author.doc_gen.stages import review_content

   final_doc = review_content(
       client=client,
       draft=draft,
       source_content=source_text,
       doc_type="guide",
       audience="intermediate",
       model="claude-3-sonnet-20241022",
       max_tokens=4000
   )
   ```

5. **Verify completion:**
   Confirm that each stage returns non-empty content and that the final documentation meets your quality standards.

## Key files

- `src/attune_author/doc_gen/pipeline.py` — Main orchestration and `generate_docs()` function
- `src/attune_author/doc_gen/stages.py` — Individual stage functions and outline parsing
- `src/attune_author/doc_gen/config.py` — Configuration classes and defaults
