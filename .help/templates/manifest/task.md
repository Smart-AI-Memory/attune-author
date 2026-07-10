---
type: task
name: manifest-task
feature: manifest
depth: task
generated_at: 2026-07-10T13:06:42.884008+00:00
source_hash: 7319e19c00c701c2206f1f0179319a541de2bebffab100900926738b2d9fbd66
status: generated
scaffold_hash: 81789d3553588f3efd2fe734c0b5b98ad7ca57f60994f45b5285e98bee2c114e
---

# Work with the manifest

Use the manifest module when you need to load, query, or update the `.help/features.yaml` file that maps project features to source files and doc outputs.

## Prerequisites

- Access to the project source code
- A `.help/` directory containing `features.yaml` (required by `load_manifest()`)
- Familiarity with `src/attune_author/manifest.py`

## Steps

1. **Map your goal to the right function.**
   Each function in `src/attune_author/manifest.py` owns one responsibility:
   - `load_manifest()` — load and validate `features.yaml` from a `.help/` directory. Raises `FileNotFoundError` if the file is missing and `ValueError` if the manifest or a feature entry isn't a mapping, if `'features'` isn't a mapping, if `'_docs'` isn't a list, or if a feature name is invalid.
   - `save_manifest()` — write a `FeatureManifest` back to `features.yaml`.
   - `match_files_to_features()` — match a list of changed files against feature glob patterns, returning a dict of feature names to matched files.
   - `resolve_topic()` — resolve a user query to a feature name, or `None` if no feature matches.
   - `is_safe_feature_name()` — check whether a feature name is safe to use as a path component.
   - `slugify()` — convert text to a lowercase slug for tag comparison.

2. **Read the data shapes before editing.**
   `load_manifest()` returns a `FeatureManifest` with `version`, a `features` dict of `Feature` objects, an optional `docs` list, and the loaded `path`. Each `Feature` carries `name`, `description`, `files`, `tags`, `doc_kinds`, `doc_paths`, and optional fields such as `doc_path`, `arch_path`, `doc_nav_section`, `cli_command`, and `status`. Confirm which fields your change reads or writes.

3. **Edit the function that owns the behavior.**
   Match the file's existing validation style — for example, `load_manifest()` raises `ValueError` with an `Invalid manifest at ...` message for each malformed section, so new validation should follow the same shape. If your change touches feature names, route them through `is_safe_feature_name()` rather than adding ad hoc path checks.

4. **Run the manifest tests.**
   Target them with:

   ```bash
   pytest -k "manifest"
   ```

## Verify your change

The task succeeded when:

- `pytest -k "manifest"` passes with no failures
- A round trip works: `load_manifest()` on a valid `.help/` directory returns a `FeatureManifest`, and `save_manifest()` writes it back to `features.yaml` without altering unrelated fields
- Invalid input still fails loudly — for example, a manifest whose `'features'` key is not a mapping raises `ValueError`

## Key files

- `src/attune_author/manifest.py` — the entire manifest feature: both dataclasses (`Feature`, `FeatureManifest`) and all six public functions
