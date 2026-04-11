---
type: reference
feature: bootstrap
depth: reference
generated_at: 2026-04-11T04:51:52.587262+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap reference

## Classes

| Class | Description |
|-------|-------------|
| `ProposedFeature` | A feature discovered by scanning |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `scan_project()` | `project_root: str \| Path` | `list[ProposedFeature]` | Scan a project and propose features |
| `proposals_to_manifest()` | `proposals: list[ProposedFeature]` | `FeatureManifest` | Convert accepted proposals to a FeatureManifest |

## Source files

- `src/attune_author/bootstrap.py`

## Tags

`setup`, `scanning`, `manifest`
