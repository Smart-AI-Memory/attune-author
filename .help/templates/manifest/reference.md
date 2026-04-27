---
type: reference
feature: manifest
depth: reference
generated_at: 2026-04-26T19:47:47.883498+00:00
source_hash: 83a32541b2c8d0a608f767253efe855779cf22ea2a49e097f1c34012c2
status: generated
---

# Manifest reference

Load, validate, and manage feature manifest files that map source code to help templates.

## Source files

- `src/attune_author/manifest.py`

## Tags

`configuration`, `yaml`, `features`

## Exports

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `is_safe_feature_name` | `name: str` | `bool` | Check if a feature name follows safe naming conventions |
| `load_manifest` | `path: str` | `FeatureManifest` | Load and parse a manifest YAML file |
| `match_files_to_features` | `files: list[str], manifest: FeatureManifest` | `dict[str, str]` | Map source files to their declared features |
| `resolve_topic` | `topic: str, manifest: FeatureManifest` | `Feature | None` | Find the feature that handles a given topic |
| `save_manifest` | `manifest: FeatureManifest, path: str` | `None` | Write a feature manifest to a YAML file |
| `slugify` | `text: str` | `str` | Convert text to a URL-safe slug |

## Classes

| Class | Description |
|---|---|
| `Feature` | Single feature definition with source files and help metadata |
| `FeatureManifest` | Collection of features with validation and lookup methods |
| `Manifest` | Root manifest containing feature definitions and global settings |

## Constants

| Constant | Values | Description |
|---|---|---|
| `_MANIFEST_VERSION` | `"1.0"` | Current manifest file format version |
