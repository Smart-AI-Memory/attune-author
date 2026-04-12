---
type: reference
feature: bootstrap
depth: reference
generated_at: 2026-04-12T04:19:17.895639+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap reference

## Classes

| Class | Description |
|-------|-------------|
| `ProposedFeature` | A feature discovered by scanning |

## Functions

| Function | Description | Parameters | Returns |
|----------|-------------|------------|---------|
| `scan_project()` | Scan a project and propose features | `project_root: str \| Path` | `list[ProposedFeature]` |
| `proposals_to_manifest()` | Convert accepted proposals to a FeatureManifest | `proposals: list[ProposedFeature]` | `FeatureManifest` |
