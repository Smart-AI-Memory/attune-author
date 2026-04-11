---
type: reference
feature: doc-gen-pipeline
depth: reference
generated_at: 2026-04-11T05:00:31.340215+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Doc Gen Pipeline reference

## Classes

| Class | Description | File |
|-------|-------------|------|
| `DocGenResult` | Document generation result containing output and metadata | `src/attune_author/doc_gen/pipeline.py` |
| `DocGenConfig` | Pipeline configuration settings for document generation | `src/attune_author/doc_gen/config.py` |

## Functions

### Pipeline orchestration

| Function | Description | File |
|----------|-------------|------|
| `generate_docs(target, config, output_path)` | Orchestrates the full documentation generation workflow | `src/attune_author/doc_gen/pipeline.py` |

### Generation stages

| Function | Description | File |
|----------|-------------|------|
| `build_outline(client, source_content, doc_type, audience, model, max_tokens)` | Creates structured outline from source content | `src/attune_author/doc_gen/stages.py` |
| `write_content(client, outline, source_content, doc_type, audience, model, max_tokens, section_focus)` | Generates documentation content from outline | `src/attune_author/doc_gen/stages.py` |
| `review_content(client, draft, source_content, doc_type, audience, model, max_tokens)` | Reviews and improves draft documentation | `src/attune_author/doc_gen/stages.py` |

### Utilities

| Function | Description | File |
|----------|-------------|------|
| `parse_outline_sections(outline)` | Extracts section titles from outline text | `src/attune_author/doc_gen/stages.py` |

## Source files

- `src/attune_author/doc_gen/pipeline.py`
- `src/attune_author/doc_gen/stages.py`
- `src/attune_author/doc_gen/config.py`

## Tags

`doc-gen`, `pipeline`, `llm`, `multi-stage`
