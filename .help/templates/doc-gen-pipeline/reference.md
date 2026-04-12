---
type: reference
feature: doc-gen-pipeline
depth: reference
generated_at: 2026-04-12T04:21:15.544790+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Doc Gen Pipeline reference

## Classes

| Class | Description | File |
|-------|-------------|------|
| `DocGenResult` | Result of document generation | `src/attune_author/doc_gen/pipeline.py` |
| `DocGenConfig` | Configuration for the document generation pipeline | `src/attune_author/doc_gen/config.py` |

## Functions

| Function | Parameters | Description | File |
|----------|------------|-------------|------|
| `generate_docs()` | `target: str, config: DocGenConfig \| None = None, output_path: str \| None = None` | Generate documentation for a source file or content | `src/attune_author/doc_gen/pipeline.py` |
| `build_outline()` | `client: Anthropic, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int` | Generate a structured documentation outline | `src/attune_author/doc_gen/stages.py` |
| `write_content()` | `client: Anthropic, outline: str, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int, section_focus: list[str] \| None = None` | Write documentation content from an outline | `src/attune_author/doc_gen/stages.py` |
| `review_content()` | `client: Anthropic, draft: str, source_content: str, doc_type: str, audience: str, model: str, max_tokens: int` | Review and polish draft documentation | `src/attune_author/doc_gen/stages.py` |
| `parse_outline_sections()` | `outline: str` | Parse top-level section titles from an outline | `src/attune_author/doc_gen/stages.py` |

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

## Tags

`doc-gen`, `pipeline`, `llm`, `multi-stage`
