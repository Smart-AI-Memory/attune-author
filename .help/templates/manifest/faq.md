---
type: faq
feature: manifest
depth: faq
generated_at: 2026-04-14T16:07:35.124044+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest FAQ

## What is the manifest feature?

The manifest feature parses and queries the `.help/features.yaml` file that defines your project's features and maps them to source files.

## When should I use it?

Use the manifest feature when you need to:
- Load project feature definitions from `features.yaml`
- Find which features are affected by file changes
- Validate feature names for safety
- Resolve user queries to specific features

## What's the main entry point?

Start with these key functions based on your task:

- `load_manifest()` — Load and parse the features.yaml file
- `match_files_to_features()` — Find which features are affected by changed files
- `resolve_topic()` — Convert user queries into feature names
- `save_manifest()` — Write feature definitions back to disk

Each function's docstring explains its inputs and outputs in detail.

## How do feature names get validated?

The `is_safe_feature_name()` function checks that feature names don't contain path separators (`/`, `\`), parent directory references (`..`), or null bytes that could cause file system issues.

## What happens if the manifest file is invalid?

`load_manifest()` raises specific `ValueError` exceptions for common problems:
- Missing or malformed YAML structure
- Invalid feature names
- Features that aren't properly formatted as mappings

## How do I debug manifest issues?

Run `pytest -k "manifest" -v` to check that the basic functionality works. If tests pass but you're still having problems, add debug logging at the point where your code fails and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
