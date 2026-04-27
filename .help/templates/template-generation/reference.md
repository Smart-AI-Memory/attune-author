---
type: reference
feature: template-generation
depth: reference
generated_at: 2026-04-26T19:46:47.168872+00:00
source_hash: e3ad2679109ec5bb81db1607254855a0f32feadedbce291531797eb11bf09912
status: generated
---

# Template Generation reference

Generate help documentation templates from source code analysis.

## Classes

| Class | Description |
|-------|-------------|
| `GeneratedTemplate` | Result of generating one template file |
| `GenerationResult` | Result of generating templates for a feature |

### GeneratedTemplate

| Field | Type | Default |
|-------|------|---------|
| `feature` | `str` | |
| `depth` | `str` | |
| `path` | `Path` | |
| `source_hash` | `str` | |

### GenerationResult

| Field | Type | Default |
|-------|------|---------|
| `feature` | `str` | |
| `templates` | `list[GeneratedTemplate]` | `field(default_factory=list)` |
| `source_hash` | `str` | `''` |
| `matched_files` | `list[str]` | `field(default_factory=list)` |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `generate_feature_templates` | `feature: Feature, help_dir: str \| Path, project_root: str \| Path, depths: list[str] \| None = None, overwrite: bool = False, use_rag: bool = True` | `GenerationResult` | Generate help templates for a feature |

### Raises

| Function | Exception | Message |
|----------|-----------|---------|
| `generate_feature_templates` | `ValueError` | `'Invalid feature name: {...}'` |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_CORE_DEPTH_NAMES` | `'concept'`, `'task'`, `'reference'` | Core depth names |
| `_PROBLEM_TEMPLATE_NAMES` | `'error'`, `'warning'`, `'troubleshooting'`, `'faq'` | Problem template names |
| `_GUIDANCE_TEMPLATE_NAMES` | `'quickstart'`, `'tip'`, `'note'`, `'comparison'` | Guidance template names |
| `_PROJECT_DOC_NAMES` | `'how-to'`, `'tutorial'`, `'cli-reference'`, `'architecture'` | Project doc names |
