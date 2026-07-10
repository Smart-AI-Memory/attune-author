---
type: concept
name: manifest-concept
feature: manifest
depth: concept
generated_at: 2026-07-10T13:06:42.873943+00:00
source_hash: 7319e19c00c701c2206f1f0179319a541de2bebffab100900926738b2d9fbd66
status: generated
scaffold_hash: d82b0ddb584116048eec72ce542512d814977f5584cb511a355093b6171d14c8
---

# Manifest

The manifest is a `features.yaml` file in your project's `.help/` directory that maps each project feature to its source files, tags, and documentation outputs. The `attune_author.manifest` module parses this file, validates it, and answers questions like "which feature owns this changed file?" and "which feature does this user query refer to?"

## Structure and lifecycle

The manifest round-trips through two dataclasses:

- **`Feature`** — one entry in the manifest. Each feature has a `name`, a `description`, and a `files` list of glob patterns identifying the source files it owns. Optional fields describe its documentation footprint: `doc_kinds` and `doc_paths` list the generated docs, `arch_path` points to an architecture doc, `doc_nav_section` places docs in navigation, and `cli_command` names an associated command. The `status` field defaults to `'auto'`, distinguishing auto-generated entries from ones you've curated.
- **`FeatureManifest`** — the parsed file as a whole: a `version` number, a `features` mapping from feature name to `Feature`, a project-level `docs` list, and the `path` the manifest was loaded from.

You load a manifest with `load_manifest(help_dir)`, which reads `features.yaml` and validates its shape. Malformed input fails fast with a `ValueError` — for example, if the top level isn't a mapping, if `'features'` isn't a mapping, or if a feature name is unsafe. A missing file raises `FileNotFoundError`. After you modify a manifest in memory, `save_manifest` writes it back to `features.yaml` and returns the path it wrote.

## Query and matching functions

Once loaded, a `FeatureManifest` supports two lookups that other parts of the system depend on:

- **`match_files_to_features(changed_files, manifest)`** — matches a list of changed file paths against each feature's glob patterns and returns a mapping from feature name to the files that hit. This is how a code change gets attributed to the features whose docs may need regeneration.
- **`resolve_topic(query, manifest)`** — resolves a free-text user query to a feature name, or returns `None` if nothing matches. `slugify` normalizes text to a lowercase slug so queries and tags compare consistently.

Because feature names become path components (for example, when writing per-feature doc files), `is_safe_feature_name` rejects names containing path traversal tokens such as `/`, `\`, or `..`. `load_manifest` applies this check during validation, so a hostile or mistyped feature name never reaches the filesystem.

## Interfaces other code uses

| Interface | Purpose | File |
|-----------|---------|------|
| `Feature` | A project feature mapped to source files and optional doc outputs | `src/attune_author/manifest.py` |
| `FeatureManifest` | The parsed `features.yaml` manifest | `src/attune_author/manifest.py` |
| `load_manifest` / `save_manifest` | Read and write `features.yaml` with validation | `src/attune_author/manifest.py` |
| `match_files_to_features` | Attribute changed files to owning features | `src/attune_author/manifest.py` |
| `resolve_topic` | Map a user query to a feature name | `src/attune_author/manifest.py` |

If you're consuming manifest data, treat `FeatureManifest` as the single source of truth for what features exist and which files they own — load it once with `load_manifest` rather than parsing `features.yaml` directly.
