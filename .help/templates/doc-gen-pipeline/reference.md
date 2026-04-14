---
type: reference
feature: doc-gen-pipeline
depth: reference
generated_at: 2026-04-14T16:18:17.690202+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline reference

Generate documentation through a multi-stage pipeline that creates outlines, writes content, and reviews drafts.

## Classes

### DocGenResult

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `content` | `str` | `''` | Final generated documentation content |
| `outline` | `str` | `''` | Documentation outline from the first stage |
| `draft` | `str` | `''` | Draft content from the writing stage |
| `stages_completed` | `list[str]` | `field(default_factory=list)` | Names of completed pipeline stages |
| `source_path` | `str` | `''` | Path to the source file that was processed |

### DocGenConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `doc_type` | `str` | `'api-reference'` | Type of documentation to generate |
| `audience` | `str` | `'developers'` | Target audience for the documentation |
| `model` | `str` | `'claude-sonnet-4-20250514'` | AI model to use for generation |
| `max_outline_tokens` | `int` | `1000` | Token limit for outline generation |
| `max_write_tokens` | `int` | `8000` | Token limit for content writing |
| `max_review_tokens` | `int` | `8000` | Token limit for content review |
| `sections_per_chunk` | `int` | `4` | Number of sections to process per chunk |
| `section_focus` | `list[str]` | `field(default_factory=list)` | Specific sections to emphasize |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `generate_docs` | `target: str, config: DocGenConfig \| None = None, output_path: str \| None = None` | `DocGenResult` | Generate documentation for a source file or content |
| `build_outline` | `client: Anthropic, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int` | `str` | Generate a structured documentation outline |
| `write_content` | `client: Anthropic, outline: str, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int, section_focus: list[str] \| None = None` | `str` | Write documentation content from an outline |
| `review_content` | `client: Anthropic, draft: str, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int` | `str` | Review and polish draft documentation |
| `parse_outline_sections` | `outline: str` | `list[str]` | Parse top-level section titles from an outline |

### Raises

| Function | Exception | Message |
|----------|-----------|---------|
| `generate_docs` | `AnthropicCallError` | `"{...} — install with: pip install 'attune-author[ai]'"` |

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

## Tags

`doc-gen`, `pipeline`, `llm`, `multi-stage`
