---
type: reference
feature: template-generation
depth: reference
generated_at: 2026-04-12T04:18:15.645794+00:00
source_hash: fac9c2bf60f422bb00b839a6c2ae022747745371b4a85621dd89daba9515f706
status: generated
---

# Template Generation reference

## Classes

| Class | Description |
|-------|-------------|
| `GeneratedTemplate` | Represents the result of generating a single template file |
| `GenerationResult` | Contains the results of generating all templates for a feature |

## Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `generate_feature_templates()` | Generates help templates for a feature from source code analysis | `feature` (Feature), `help_dir` (str \| Path), `project_root` (str \| Path), `depths` (list[str] \| None), `overwrite` (bool) |

## Source files

- `src/attune_author/generator.py`

## Tags

`generation`, `jinja2`, `ast`, `meta-templates`
