---
type: error
feature: doc-gen-pipeline
depth: error
generated_at: 2026-04-14T16:18:27.337774+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline errors

Documentation generation pipeline failures occur during the three-stage process of outline creation, content writing, and review.

## Common error signatures

**Missing AI dependencies:**
```
AnthropicCallError: ... — install with: pip install 'attune-author[ai]'
```

**API communication failures:**
- Connection timeouts during any of the three generation stages
- Authentication errors with the Anthropic API
- Token limit exceeded errors when `max_*_tokens` config is too high

**Content processing errors:**
- Empty or malformed outlines that can't be parsed by `parse_outline_sections()`
- Source files that can't be read or contain unsupported content formats

## Where errors originate

Pipeline failures typically occur at these stage boundaries:

- `generate_docs()` — Main orchestrator that coordinates all three stages and handles file I/O
- `build_outline()` — First stage that structures the documentation plan
- `write_content()` — Second stage that produces draft content from the outline
- `review_content()` — Final stage that polishes the draft
- `parse_outline_sections()` — Utility that extracts section headers for chunked processing

Each stage depends on the previous one's output, so early failures cascade through the entire pipeline.

## How to diagnose

1. **Check for AI dependencies.** If you see `AnthropicCallError` about missing installations, run `pip install 'attune-author[ai]'` to install the Anthropic client.

2. **Verify your configuration.** Examine the `DocGenConfig` settings, especially token limits. If any `max_*_tokens` value exceeds the model's context window, the API will reject the request.

3. **Identify the failing stage.** Check `DocGenResult.stages_completed` to see which stages succeeded. If `['outline']` is present but `['outline', 'write']` is not, the failure occurred during content writing.

4. **Test with simpler inputs.** Try generating documentation for a smaller source file. Large files may hit token limits or timeout during processing.

5. **Check file permissions.** If `output_path` is specified, verify you can write to that location. Pipeline failures often stem from filesystem access issues.

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

**Tags:** `doc-gen`, `pipeline`, `llm`, `multi-stage`
