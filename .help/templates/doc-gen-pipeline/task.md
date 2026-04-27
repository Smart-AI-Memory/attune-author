---
type: task
feature: doc-gen-pipeline
depth: task
generated_at: 2026-04-26T19:50:08.962814+00:00
source_hash: ed1e0ee4f61601566ddf49801a234a64d93605b2683aafe5ee4f86d48d8dd885
status: generated
---

# Work with doc gen pipeline

Use the doc gen pipeline when you need high-quality documentation generated through a three-stage process: outline creation, content writing, and review.

## Prerequisites

- Access to the project source code
- An Anthropic API key configured for AI-powered generation
- Understanding of the target documentation type (api-reference, quickstart, etc.)

## Configure the pipeline

1. **Set up DocGenConfig with your requirements:**
   ```python
   from attune_author.doc_gen.config import DocGenConfig

   config = DocGenConfig(
       doc_type='api-reference',
       audience='developers',
       max_outline_tokens=1000,
       sections_per_chunk=4
   )
   ```

2. **Choose your documentation type:**
   - Use `'api-reference'` for comprehensive function and class documentation
   - Use `'quickstart'` for getting-started guides
   - Use `'tutorial'` for step-by-step learning materials

## Generate documentation

1. **Call the main pipeline function:**
   ```python
   from attune_author.doc_gen.pipeline import generate_docs

   result = generate_docs(
       target='path/to/source.py',
       config=config,
       output_path='docs/output.md'
   )
   ```

2. **Verify each stage completed:**
   Check `result.stages_completed` contains `['outline', 'write', 'review']`.

3. **Review the generated content:**
   The final documentation is in `result.content`, with intermediate artifacts in `result.outline` and `result.draft`.

## Customize generation stages

1. **Focus on specific sections:**
   ```python
   config.section_focus = ['Installation', 'Quick Start', 'API Reference']
   ```

2. **Adjust token limits for longer content:**
   ```python
   config.max_write_tokens = 12000  # For comprehensive guides
   config.max_review_tokens = 10000  # For thorough editing
   ```

3. **Control chunking for large documents:**
   ```python
   config.sections_per_chunk = 2  # Process fewer sections at once
   ```

## Troubleshoot common issues

1. **If generation fails with AnthropicCallError:**
   Install the AI dependencies: `pip install 'attune-author[ai]'`

2. **If output is incomplete:**
   Increase `max_write_tokens` or reduce `sections_per_chunk` to handle complex content.

3. **If outline doesn't match expectations:**
   Review the `result.outline` and adjust `section_focus` to target specific areas.

## Verify success

The pipeline succeeds when:
- `result.stages_completed` includes all three stages
- `result.content` contains well-structured documentation
- The output file (if specified) exists and contains the generated content
