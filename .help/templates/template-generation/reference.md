---
type: reference
feature: template-generation
depth: reference
generated_at: 2026-04-14T16:02:39.418001+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation reference

Generate help templates from source code analysis and configurable depth levels.

## Classes

### GeneratedTemplate

Result of generating one template file.

| Field | Type | Default |
|-------|------|---------|
| feature | str | |
| depth | str | |
| path | Path | |
| source_hash | str | |

### GenerationResult

Result of generating templates for a feature.

| Field | Type | Default |
|-------|------|---------|
| feature | str | |
| templates | list[GeneratedTemplate] | field(default_factory=list) |
| source_hash | str | '' |
| matched_files | list[str] | field(default_factory=list) |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `generate_feature_templates` | feature: Feature, help_dir: str \| Path, project_root: str \| Path, depths: list[str] \| None = None, overwrite: bool = False | GenerationResult | Generate help templates for a feature |

### Raises

| Exception | Message |
|-----------|---------|
| ValueError | 'Invalid feature name: {...}' |

## Constants

### Core depth names

| Constant | Values |
|----------|--------|
| `_CORE_DEPTH_NAMES` | 'concept', 'task', 'reference' |

### Problem template names

| Constant | Values |
|----------|--------|
| `_PROBLEM_TEMPLATE_NAMES` | 'error', 'warning', 'troubleshooting', 'faq' |

### Guidance template names

| Constant | Values |
|----------|--------|
| `_GUIDANCE_TEMPLATE_NAMES` | 'quickstart', 'tip', 'note', 'comparison' |
