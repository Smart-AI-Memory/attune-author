---
type: note
feature: manifest
depth: note
generated_at: 2026-04-14T16:07:57.236788+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Note: manifest

## Context

The manifest module handles the `.help/features.yaml` file that maps project features to source files. This file serves as the central registry for organizing help documentation around features rather than individual files.

## Content

The manifest system provides two core data classes and several utility functions for working with feature definitions:

**Data classes:**
- `Feature` — Represents a single project feature with name, description, file patterns, and tags
- `FeatureManifest` — Contains the parsed manifest with version info and feature dictionary

**Key functions:**
- `load_manifest()` — Reads and validates the features.yaml file with comprehensive error handling
- `save_manifest()` — Writes manifest data back to the yaml file
- `match_files_to_features()` — Maps changed source files to their corresponding features using glob patterns
- `resolve_topic()` — Translates user queries into specific feature names
- `is_safe_feature_name()` — Validates feature names for filesystem safety

The module enforces strict validation when loading manifests, checking for proper YAML structure, valid feature names, and required fields. Feature names must avoid unsafe path components like `/`, `\`, `..`, and null bytes.

## Source files

- `src/attune_author/manifest.py`

**Tags:** `configuration`, `yaml`, `features`
