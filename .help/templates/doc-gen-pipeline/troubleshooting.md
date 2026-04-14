---
type: troubleshooting
feature: doc-gen-pipeline
depth: troubleshooting
generated_at: 2026-04-14T16:18:56.626578+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Troubleshoot doc gen pipeline

## Before you start

The doc gen pipeline generates documentation through three sequential stages: outline generation, content writing, and review. Each stage uses LLM calls that can fail independently. Most issues stem from API connectivity, malformed inputs, or token limit exceeded errors.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `AnthropicCallError` raised | Run `pip show anthropic` to verify the package is installed with the `[ai]` extra |
| Empty `content` field in result | Examine the `stages_completed` list to see which stage failed |
| Truncated or incomplete output | Compare your input size against `max_outline_tokens`, `max_write_tokens`, or `max_review_tokens` limits |
| Outline parsing errors | Inspect the raw outline string for malformed section headers |
| Slow generation (>30s per stage) | Check your `model` setting and current API latency |

## Step-by-step diagnosis

1. **Test with minimal input.**
   Create a small test file and call `generate_docs()` with default settings:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs
   result = generate_docs("test.py")
   print(f"Stages completed: {result.stages_completed}")
   ```

2. **Check API connectivity.**
   Verify your Anthropic API key is set and valid:
   ```bash
   python -c "from anthropic import Anthropic; Anthropic().messages.create(model='claude-3-sonnet-20240229', max_tokens=10, messages=[{'role': 'user', 'content': 'test'}])"
   ```

3. **Examine stage progression.**
   Look at the `DocGenResult.stages_completed` field to identify where the pipeline stopped:
   - Missing "outline": `build_outline()` failed
   - Missing "write": `write_content()` failed
   - Missing "review": `review_content()` failed

4. **Validate configuration.**
   Check your `DocGenConfig` values against the documented limits:
   ```python
   config = DocGenConfig(max_write_tokens=16000)  # May exceed model limits
   ```

5. **Test individual stages.**
   Run each stage function directly to isolate the failure:
   ```python
   from attune_author.doc_gen.stages import build_outline
   from anthropic import Anthropic
   client = Anthropic()
   outline = build_outline(client, source_content, "api-reference", "developers", "claude-3-sonnet-20240229", 1000)
   ```

## Common fixes

- **Install AI dependencies:** If you see `AnthropicCallError`, install the full package:
  ```bash
  pip install 'attune-author[ai]'
  ```

- **Reduce token limits:** For large source files, lower the token limits in your config:
  ```python
  config = DocGenConfig(max_write_tokens=4000, sections_per_chunk=2)
  ```

- **Set section focus:** For partial generation, specify which sections to prioritize:
  ```python
  config = DocGenConfig(section_focus=["Parameters", "Returns", "Examples"])
  ```

- **Switch models:** If rate-limited, try a different model:
  ```python
  config = DocGenConfig(model="claude-3-haiku-20240307")
  ```

- **Check source file encoding:** Ensure your target file uses UTF-8 encoding, especially if it contains non-ASCII characters.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
