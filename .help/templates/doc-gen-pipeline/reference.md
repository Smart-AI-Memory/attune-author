---
type: reference
feature: doc-gen-pipeline
depth: reference
generated_at: 2026-04-26T19:50:22.310414+00:00
source_hash: ed1e0ee4f61601566ddf49801a234a64d93605b2683aafe5ee4f86d48d8dd885
status: generated
---

# Doc Gen Pipeline reference

Generate documentation through a three-stage pipeline: outline, write, and review. Configure documentation type, audience, and model parameters to produce API references, README sections, or docstrings from source code.

## Classes

| Class | Description |
|-------|-------------|
| `DocGenConfig` | Configuration for the document generation pipeline |
| `DocGenResult` | Result of document generation with content and pipeline stages |

### DocGenConfig fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `doc_type` | `str` | `'api-reference'` | Type of documentation to generate |
| `audience` | `str` | `'developers'` | Target audience for the documentation |
| `model` | `str` | `'claude-sonnet-4-20250514'` | AI model to use for generation |
| `max_outline_tokens` | `int` | `1000` | Token limit for outline generation |
| `max_write_tokens` | `int` | `8000` | Token limit for content writing |
| `max_review_tokens` | `int` | `8000` | Token limit for content review |
| `sections_per_chunk` | `int` | `4` | Number of sections to process per chunk |
| `section_focus` | `list[str]` | `field(default_factory=list)` | Specific sections to focus on during generation |

### DocGenResult fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `content` | `str` | `''` | Final generated documentation content |
| `outline` | `str` | `''` | Structured outline created in stage one |
| `draft` | `str` | `''` | Draft content from stage two |
| `stages_completed` | `list[str]` | `field(default_factory=list)` | Pipeline stages that completed successfully |
| `source_path` | `str` | `''` | Path to the source file or content |

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
| `generate_docs` | `AnthropicCallError` | `{...} — install with: pip install 'attune-author[ai]'` |
