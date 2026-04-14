---
type: concept
feature: bootstrap
depth: concept
generated_at: 2026-04-14T14:03:21.168342+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap

Bootstrap scans a project directory to automatically discover potential features and generate an initial feature manifest.

## Discovery process

The bootstrap system walks through your project files, identifying meaningful components based on common patterns:

- **Entry points** like `main.py`, `app.py`, or `cli.py` suggest command-line or application features
- **Configuration patterns** in filenames containing "config", "settings", or "conf" indicate setup features
- **Directory structure** reveals organizational boundaries that often correspond to feature boundaries

During scanning, bootstrap skips common non-feature directories like `.git`, `__pycache__`, `node_modules`, and virtual environments.

## Feature proposals

Each discovered feature becomes a `ProposedFeature` with:

- A descriptive name derived from file or directory names
- Associated source files that implement the feature
- Confidence level (defaults to "medium") indicating how certain the detection is
- Tags for categorization
- A reason explaining why this grouping was proposed

For example, scanning a Django project might propose separate features for models, views, and management commands based on the standard project layout.

## Manifest generation

You can convert accepted proposals into a working `FeatureManifest` using `proposals_to_manifest()`. This transforms the discovery results into the structured format needed by other parts of the system.

The bootstrap process gives you a starting point for feature organization rather than requiring manual manifest creation from scratch.
