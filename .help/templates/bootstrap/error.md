---
type: error
feature: bootstrap
depth: error
generated_at: 2026-04-14T14:03:46.012270+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap errors

Project scanning and manifest generation failures occur when the bootstrap module cannot analyze your project structure or convert feature proposals into a valid manifest.

## Common error signatures

- `FileNotFoundError` - Project root path does not exist or is inaccessible
- `PermissionError` - Cannot read directories or files during project scan
- `ValueError` - Invalid project structure or malformed feature proposals
- `AttributeError` - Missing required fields when converting proposals to manifest

## Where errors originate

Bootstrap errors come from two main functions:

- `scan_project()` - Fails when traversing directories, reading files, or analyzing project structure
- `proposals_to_manifest()` - Fails when validating or converting ProposedFeature objects to FeatureManifest format

## How to diagnose

1. **Verify project path exists and is readable.** The most common cause is passing a non-existent or inaccessible project root to `scan_project()`.

2. **Check directory permissions.** Bootstrap skips protected directories but needs read access to the project root and discoverable subdirectories.

3. **Validate ProposedFeature data.** If `proposals_to_manifest()` fails, inspect the proposals list for missing required fields (name, description) or invalid confidence values.

4. **Review excluded directories.** Bootstrap automatically skips common build and cache directories. If your project structure conflicts with the exclusion patterns in `_SKIP_DIRS`, this may affect feature discovery.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
