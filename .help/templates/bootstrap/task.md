---
type: task
feature: bootstrap
depth: task
generated_at: 2026-04-14T14:03:30.154713+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Work with bootstrap

Use bootstrap when you need to automatically generate a feature manifest by scanning a project's directory structure and identifying Python packages, entry points, and configuration files.

## Prerequisites

- Access to the project source code
- Python project with standard directory layout
- Familiarity with `src/attune_author/bootstrap.py`

## Scan a project for features

1. **Call the scan function with your project path.**
   ```python
   from attune_author.bootstrap import scan_project

   proposals = scan_project("/path/to/your/project")
   ```

2. **Review the proposed features.**
   Each `ProposedFeature` includes:
   - Feature name and description
   - Associated files
   - Confidence level (low, medium, high)
   - Discovery reasoning

3. **Filter proposals by confidence if needed.**
   ```python
   high_confidence = [p for p in proposals if p.confidence == 'high']
   ```

## Convert proposals to manifest

1. **Generate the manifest from accepted proposals.**
   ```python
   from attune_author.bootstrap import proposals_to_manifest

   manifest = proposals_to_manifest(proposals)
   ```

2. **Save the manifest to your project.**
   ```python
   with open('.help/features.yaml', 'w') as f:
       f.write(manifest.to_yaml())
   ```

## Verify the results

Check that the generated manifest includes expected features by examining:
- Entry point files (main.py, app.py, cli.py, etc.)
- Configuration modules matching patterns like "config", "settings", "conf"
- Python packages with meaningful directory structures

The bootstrap skips common build and cache directories defined in `_SKIP_DIRS`.

## Key files

- `src/attune_author/bootstrap.py` — Main scanning and conversion logic
