---
type: concept
feature: bootstrap
depth: concept
generated_at: 2026-04-14T16:08:15.813184+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap

Bootstrap automatically discovers features in a codebase by scanning directory structures and file patterns, then generates an initial feature manifest.

## Discovery process

The scanner examines your project's file system to identify potential features based on:

- **Entry points** — Files like `main.py`, `app.py`, `cli.py`, `server.py` that typically contain application logic
- **Configuration patterns** — Directories and files containing "config", "settings", or "conf" in their names
- **Directory structure** — Organized code folders that suggest distinct functionality

The scanner skips common directories that don't contain feature code, such as `.git`, `__pycache__`, `node_modules`, and virtual environments.

## Feature proposals

Each discovered feature becomes a `ProposedFeature` with these attributes:

- **name** — Derived from directory or file names
- **description** — Generated based on the context where the feature was found
- **files** — List of relevant source files associated with the feature
- **tags** — Categorization labels to help organize features
- **confidence** — Assessment of how certain the scanner is about the feature (defaults to 'medium')
- **reason** — Explanation of why this was identified as a feature

## Manifest generation

After scanning, you can convert the feature proposals into a structured `FeatureManifest` using `proposals_to_manifest()`. This creates the foundation for documentation generation and project analysis workflows.

The bootstrap process gives you a starting point that you can refine by accepting, rejecting, or modifying the proposed features before generating your final documentation.
