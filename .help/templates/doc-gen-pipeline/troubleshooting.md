---
type: troubleshooting
feature: doc-gen-pipeline
depth: troubleshooting
generated_at: 2026-04-14T14:13:57.828638+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Troubleshoot doc gen pipeline

## Before you start

The doc gen pipeline generates documentation through three stages: outline, write, and review. Each stage calls an LLM model to progressively refine content from source code into polished documentation.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `AnthropicCallError` exception | Missing AI dependencies - install with `pip install 'attune-author[ai]'` |
| Empty `DocGenResult.content` | Check if all three stages completed in `stages_completed` field |
| Partial content generation | Verify `max_*_tokens` limits in config aren't too restrictive |
| Wrong documentation type | Confirm `doc_type` in `DocGenConfig` matches your target format |
| Slow generation | Check `sections_per_chunk` - lower values increase API calls but reduce per-call latency |

## Step-by-step diagnosis

1. **Verify AI dependencies are installed.**
   The pipeline requires Anthropic's Claude model. Install missing dependencies:
   ```bash
   pip install 'attune-author[ai]'
   ```

2. **Test with minimal configuration.**
   Create a basic `DocGenConfig` and generate docs for a simple source file:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs, DocGenConfig

   config = DocGenConfig()  # Uses defaults
   result = generate_docs("path/to/simple_file.py", config)
   print(f"Completed stages: {result.stages_completed}")
   ```

3. **Check stage progression.**
   Examine the `DocGenResult` to see which stages completed:
   - `outline` stage creates structured documentation plan
   - `write` stage generates content from outline
   - `review` stage polishes the draft

   If stages fail partway through, the issue is likely in token limits or model availability.

4. **Validate configuration parameters.**
   Check your `DocGenConfig` values:
   - `max_outline_tokens`, `max_write_tokens`, `max_review_tokens` - increase if content gets truncated
   - `sections_per_chunk` - reduce if hitting rate limits, increase if generation is slow
   - `model` - ensure the specified Claude model is available

5. **Enable debug logging for LLM calls.**
   Set logging to DEBUG level to see API request/response details:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Common fixes

- **Install AI dependencies.** Run `pip install 'attune-author[ai]'` if you get `AnthropicCallError` about missing packages.

- **Increase token limits.** If content gets cut off, raise the relevant limit in `DocGenConfig`:
  ```python
  config = DocGenConfig(
      max_outline_tokens=1500,
      max_write_tokens=12000,
      max_review_tokens=10000
  )
  ```

- **Adjust chunking for rate limits.** If you hit API rate limits, reduce `sections_per_chunk`:
  ```python
  config = DocGenConfig(sections_per_chunk=2)
  ```

- **Focus on specific sections.** Use `section_focus` to generate only the sections you need:
  ```python
  config = DocGenConfig(section_focus=["Parameters", "Examples"])
  ```

- **Verify source file exists.** Check that the target file path is valid and readable before calling `generate_docs()`.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
