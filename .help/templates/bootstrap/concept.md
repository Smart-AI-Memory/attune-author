---
type: concept
feature: bootstrap
depth: concept
generated_at: 2026-04-12T04:19:04.052489+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap

Bootstrap analyzes your Python project structure to automatically generate an initial feature manifest.

## Core process

Bootstrap scans your project directory and proposes features based on what it finds in your Python packages and file structure. The `scan_project()` function walks through your project root and creates `ProposedFeature` objects for each potential feature it discovers. You can then convert these proposals into a complete `FeatureManifest` using `proposals_to_manifest()`.

## Key components

- **`ProposedFeature`** — Represents a feature that bootstrap discovered during project scanning, containing the feature's suggested name and configuration
- **`scan_project()`** — Analyzes a project directory and returns a list of proposed features based on the Python package structure it finds
- **`proposals_to_manifest()`** — Takes your accepted proposals and converts them into a properly formatted feature manifest

## Integration points

| Interface | Purpose | File |
|-----------|---------|------|
| `ProposedFeature` | Represents discovered features for manifest generation | `src/attune_author/bootstrap.py` |
