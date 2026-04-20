---
type: reference
feature: manifest
depth: reference
generated_at: 2026-04-14T16:06:38.652788+00:00
source_hash: 9a254478123a04daeb294db1576d4b58b18d970e577f6263f65fa33be54c42ee
status: generated
---

# Manifest reference

Parse and query features.yaml manifests for project documentation.

## Classes

### Feature

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | | Feature name |
| `description` | `str` | | Human-readable description |
| `files` | `list[str]` | `[]` | File glob patterns covered by this feature |
| `tags` | `list[str]` | `[]` | Categorization tags |

### FeatureManifest

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | `int` | | Manifest format version |
| `features` | `dict[str, Feature]` | | Feature definitions by name |
| `path` | `Path \| None` | `None` | Source file path |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `is_safe_feature_name` | `name: object` | `bool` | Check whether a feature name is safe to use as a path component |
| `load_manifest` | `help_dir: str \| Path` | `FeatureManifest` | Load and validate features.yaml from a .help/ directory |
| `save_manifest` | `manifest: FeatureManifest, help_dir: str \| Path` | `Path` | Write a FeatureManifest to features.yaml |
| `match_files_to_features` | `changed_files: list[str], manifest: FeatureManifest` | `dict[str, list[str]]` | Match changed files against feature glob patterns |
| `resolve_topic` | `query: str, manifest: FeatureManifest` | `str \| None` | Resolve a user query to a feature name |

### Raises

| Function | Exception | Message |
|----------|-----------|---------|
| `load_manifest` | `FileNotFoundError` | 'No {...} in {...}' |
| `load_manifest` | `ValueError` | 'Invalid manifest at {...}: expected mapping, got {...}' |
| `load_manifest` | `ValueError` | "Invalid manifest at {...}: 'features' must be a mapping" |
| `load_manifest` | `ValueError` | 'Invalid feature name: {...}' |
| `load_manifest` | `ValueError` | "Invalid manifest at {...}: feature '{...}' must be a mapping" |

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `_MANIFEST_FILENAME` | `'features.yaml'` | Default manifest filename |
| `_UNSAFE_NAME_TOKENS` | `{'/', '\\', '..', '\x00'}` | Character patterns forbidden in feature names |
