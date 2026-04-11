---
type: concept
feature: bootstrap
depth: concept
generated_at: 2026-04-11T04:51:37.918391+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap

## How it works

Bootstrap scans your project directory to automatically detect features and generate an initial feature manifest based on your Python package structure.

The process works in two stages:

1. **Project scanning** — The `scan_project` function walks through your project directory, analyzing the structure and identifying potential features as `ProposedFeature` objects
2. **Manifest generation** — The `proposals_to_manifest` function converts your accepted feature proposals into a complete `FeatureManifest`

## Core components

- **`ProposedFeature`** — Represents a single feature that the scanner discovered in your codebase, containing the metadata needed to decide whether to include it in your final manifest

## Integration points

Bootstrap connects to the broader workflow through its manifest output, which becomes the foundation for feature documentation and project setup.
