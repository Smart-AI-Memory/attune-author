---
type: task
feature: bootstrap
depth: task
generated_at: 2026-04-14T16:08:25.609534+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Work with bootstrap

Use bootstrap when you need to automatically generate a feature manifest by scanning an existing project's directory structure and code organization.

## Prerequisites

- Access to the project source code
- Python environment with the bootstrap module available

## Scan a project for features

1. **Import the bootstrap module:**
   ```python
   from attune_author.bootstrap import scan_project
   ```

2. **Run the project scan:**
   ```python
   proposals = scan_project("/path/to/your/project")
   ```
   The scanner examines your project structure, identifies entry points like `main.py` or `app.py`, and skips common directories like `.git`, `__pycache__`, and `node_modules`.

3. **Review the proposed features:**
   Each `ProposedFeature` includes:
   - `name`: The feature identifier
   - `description`: What the feature does
   - `files`: Associated source files
   - `confidence`: Scanner's certainty level
   - `reason`: Why this feature was proposed

## Convert proposals to manifest

1. **Filter proposals as needed:**
   Review the confidence levels and reasons to accept or reject proposals.

2. **Generate the manifest:**
   ```python
   from attune_author.bootstrap import proposals_to_manifest
   manifest = proposals_to_manifest(accepted_proposals)
   ```

3. **Verify the output:**
   The resulting `FeatureManifest` should contain only the features you want to include in your project documentation.

## Success criteria

- `scan_project()` returns a list of `ProposedFeature` objects
- Each proposal includes relevant files from your project
- The generated manifest contains structured feature definitions ready for documentation

## Key files

- `src/attune_author/bootstrap.py`
