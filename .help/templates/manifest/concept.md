---
type: concept
feature: manifest
depth: concept
generated_at: 2026-04-14T16:06:14.749377+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest

The manifest is a parser and query engine for the `.help/features.yaml` file that maps project features to their source code files.

## Core components

**Feature dataclass**
Represents a single project feature with its metadata:
- `name`: The feature identifier
- `description`: Human-readable description
- `files`: List of file paths or glob patterns associated with the feature
- `tags`: Optional labels for categorization

**FeatureManifest dataclass**
Contains the complete parsed manifest:
- `version`: Schema version for the manifest format
- `features`: Dictionary mapping feature names to Feature objects
- `path`: File system location of the source `features.yaml`

## File operations

The manifest system loads and validates `features.yaml` from `.help/` directories through `load_manifest()`, which enforces naming rules and structural requirements. You can persist changes back to disk using `save_manifest()`.

Feature names must pass safety checks via `is_safe_feature_name()` to prevent path traversal issues—names cannot contain `/`, `\`, `..`, or null bytes.

## Query capabilities

Two query functions help connect user requests to features:

- `match_files_to_features()`: Given a list of changed files, returns which features contain those files based on glob pattern matching
- `resolve_topic()`: Takes a user query string and attempts to find the corresponding feature name

These functions enable workflows like "show me help for the files I just modified" or "find documentation for the authentication system."
