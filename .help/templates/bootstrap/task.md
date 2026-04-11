---
type: task
feature: bootstrap
depth: task
generated_at: 2026-04-11T04:51:43.894637+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Work with bootstrap

Use bootstrap when you need to generate an initial feature manifest by automatically scanning your project's directory structure and Python package layout.

## Prerequisites

- Access to the project source code
- Python environment with attune_author installed

## Scan a project for features

1. **Import the bootstrap module.**
   ```python
   from attune_author.bootstrap import scan_project
   ```

2. **Run the project scan.**
   ```python
   proposals = scan_project("/path/to/your/project")
   ```
   Replace `/path/to/your/project` with your actual project root directory.

3. **Review the proposed features.**
   Each `ProposedFeature` in the returned list represents a potential feature discovered during the scan. Examine the proposals to understand what the scanner detected.

## Convert proposals to manifest

1. **Import the conversion function.**
   ```python
   from attune_author.bootstrap import proposals_to_manifest
   ```

2. **Filter your proposals (optional).**
   Remove any `ProposedFeature` objects you don't want in your final manifest.

3. **Generate the manifest.**
   ```python
   manifest = proposals_to_manifest(proposals)
   ```

4. **Verify the manifest.**
   Check that the resulting `FeatureManifest` contains the features you expect. The manifest should reflect your project's actual structure and intended feature set.

## Test your changes

Run the bootstrap-related tests to ensure your modifications work correctly:
```bash
pytest -k "bootstrap"
```

You've successfully bootstrapped your project when the generated manifest accurately represents your project's features and can be used for further development.

## Key files

- `src/attune_author/bootstrap.py` — Contains all bootstrap functionality
