---
type: task
feature: bootstrap
depth: task
generated_at: 2026-04-12T04:19:10.432869+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Work with bootstrap

Use bootstrap when you need to automatically generate an initial feature manifest by analyzing your project's directory structure and Python package layout.

## Prerequisites

- Access to the project source code
- Python environment with the bootstrap module available

## Scan a project for features

1. **Import the scanning function:**
   ```python
   from attune_author.bootstrap import scan_project
   ```

2. **Run the project scan:**
   ```python
   proposals = scan_project("/path/to/your/project")
   ```

   The function returns a list of `ProposedFeature` objects representing detected features.

3. **Review the proposals:**
   Examine each `ProposedFeature` to verify the scanner correctly identified your project's structure.

## Convert proposals to a manifest

1. **Import the conversion function:**
   ```python
   from attune_author.bootstrap import proposals_to_manifest
   ```

2. **Generate the manifest:**
   ```python
   manifest = proposals_to_manifest(proposals)
   ```

3. **Verify the output:**
   Check that the resulting `FeatureManifest` contains the expected features for your project.

## Test the bootstrap process

1. **Run bootstrap-specific tests:**
   ```bash
   pytest -k "bootstrap"
   ```

2. **Verify success:**
   All tests pass and no new test failures appear in the output.

## Key files

- `src/attune_author/bootstrap.py` — Contains `scan_project()` and `proposals_to_manifest()` functions
