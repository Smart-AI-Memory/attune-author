---
type: error
feature: manifest
depth: error
generated_at: 2026-04-14T16:06:47.813639+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest errors

Failures when loading, parsing, or querying the `.help/features.yaml` manifest file that maps project features to source files.

## Common error signatures

- `FileNotFoundError: No {...} in {...}` — The features.yaml file is missing from the .help/ directory
- `ValueError: Invalid manifest at {...}: expected mapping, got {...}` — The YAML file contains invalid structure (not a dictionary)
- `ValueError: Invalid manifest at {...}: 'features' must be a mapping` — The top-level 'features' key is missing or not a dictionary
- `ValueError: Invalid feature name: {...}` — A feature name contains unsafe path characters like `/`, `\`, `..`, or null bytes
- `ValueError: Invalid manifest at {...}: feature '{...}' must be a mapping` — A feature entry is not a dictionary with proper fields

## Where errors originate

Most manifest errors occur during loading and validation:

- `load_manifest()` validates the YAML structure and feature definitions
- `is_safe_feature_name()` rejects feature names with unsafe path components
- `save_manifest()` fails when the target directory is not writable
- `match_files_to_features()` encounters issues with malformed glob patterns
- `resolve_topic()` returns None for ambiguous or missing feature queries

## How to diagnose

1. **Check if features.yaml exists.** The manifest must be located at `.help/features.yaml` relative to your help directory. A missing file triggers `FileNotFoundError`.

2. **Validate the YAML syntax.** Parse the file manually with `yaml.safe_load()` to catch basic syntax errors before manifest validation runs.

3. **Inspect feature name safety.** Feature names cannot contain `/`, `\`, `..`, or null bytes since they become path components. Use `is_safe_feature_name()` to test specific names.

4. **Verify the manifest structure.** The file must be a dictionary with a 'features' key that maps to feature definitions. Each feature needs 'name' and 'description' fields at minimum.

5. **Test file matching patterns.** If `match_files_to_features()` fails, check that the 'files' lists in your features contain valid glob patterns that match your source tree.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
