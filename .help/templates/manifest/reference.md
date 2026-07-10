---
type: reference
name: manifest-reference
feature: manifest
depth: reference
generated_at: 2026-07-10T13:06:42.892390+00:00
source_hash: 7319e19c00c701c2206f1f0179319a541de2bebffab100900926738b2d9fbd66
status: generated
scaffold_hash: 1db9b56cd5fc76bff9ab4cd3a8cc256eda18f85b4d3db4004c983f206a9529ad
---

# Manifest reference

Load, validate, save, and query the `.help/features.yaml` manifest that maps project features to source files and doc outputs.

## Classes

| Class | Description | File |
|-------|-------------|------|
| `Feature` | A project feature mapped to source files and optional doc outputs. | `src/attune_author/manifest.py` |
| `FeatureManifest` | Parsed features.yaml manifest. | `src/attune_author/manifest.py` |

### Feature fields

| Field | Type | Default |
|-------|------|---------|
| `name` | `str` | — |
| `description` | `str` | — |
| `files` | `list[str]` | `field(default_factory=list)` |
| `tags` | `list[str]` | `field(default_factory=list)` |
| `doc_kinds` | `list[str]` | `field(default_factory=list)` |
| `doc_paths` | `list[str]` | `field(default_factory=list)` |
| `doc_path` | `str \| None` | `None` |
| `arch_path` | `str \| None` | `None` |
| `doc_nav_section` | `str \| None` | `None` |
| `cli_command` | `str \| None` | `None` |
| `status` | `str` | `'auto'` |

### FeatureManifest fields

| Field | Type | Default |
|-------|------|---------|
| `version` | `int` | — |
| `features` | `dict[str, Feature]` | — |
| `docs` | `list[str]` | `field(default_factory=list)` |
| `path` | `Path \| None` | `None` |

## Functions

| Function | Parameters | Returns | Description | File |
|----------|------------|---------|-------------|------|
| `is_safe_feature_name` | `name: object` | `bool` | Checks whether a feature name is safe to use as a path component. | `src/attune_author/manifest.py` |
| `load_manifest` | `help_dir: str \| Path` | `FeatureManifest` | Loads and validates `features.yaml` from a `.help/` directory. | `src/attune_author/manifest.py` |
| `save_manifest` | `manifest: FeatureManifest, help_dir: str \| Path` | `Path` | Writes a `FeatureManifest` to `features.yaml` and returns the written path. | `src/attune_author/manifest.py` |
| `match_files_to_features` | `changed_files: list[str], manifest: FeatureManifest` | `dict[str, list[str]]` | Matches changed files against feature glob patterns. | `src/attune_author/manifest.py` |
| `resolve_topic` | `query: str, manifest: FeatureManifest` | `str \| None` | Resolves a user query to a feature name, or `None` if no feature matches. | `src/attune_author/manifest.py` |
| `slugify` | `text: str` | `str` | Converts text to a lowercase slug for tag comparison. | `src/attune_author/manifest.py` |

### Raises

`load_manifest` raises the following exceptions:

| Exception | Message |
|-----------|---------|
| `FileNotFoundError` | `No {...} in {...}` |
| `ValueError` | `Invalid manifest at {...}: expected mapping, got {...}` |
| `ValueError` | `Invalid manifest at {...}: 'features' must be a mapping` |
| `ValueError` | `Invalid feature name: {...}` |
| `ValueError` | `Invalid manifest at {...}: feature '{...}' must be a mapping` |
| `ValueError` | `Invalid manifest at {...}: '_docs' must be a list` |

`{...}` marks values interpolated at runtime.

## Constants

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| `_MANIFEST_FILENAME` | `str` | `'features.yaml'` | Filename that `load_manifest` and `save_manifest` read and write inside the `.help/` directory. |
| `_UNSAFE_NAME_TOKENS` | `tuple` | `{'/', '\\', '..', '\x00'}` | Tokens that cause `is_safe_feature_name` to reject a feature name. |

## Source files

- `src/attune_author/manifest.py`

## Tags

`configuration`, `yaml`, `features`
