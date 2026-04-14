---
type: note
feature: bootstrap
depth: note
generated_at: 2026-04-14T16:09:45.275862+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Note: bootstrap

## Context

The bootstrap feature automatically generates an initial feature manifest by scanning your project's directory structure and file patterns. This eliminates the need to manually catalog every component when starting documentation.

## How scanning works

The `scan_project()` function walks through your project directory and identifies potential features based on:

- **Entry points**: Files like `main.py`, `app.py`, `cli.py`, `server.py`, `manage.py`, `wsgi.py`, `asgi.py`, `index.ts`, `index.js`, `main.go`, and `main.rs`
- **Configuration patterns**: Files or directories containing "config", "settings", or "conf"
- **Directory structure**: Python packages, modules, and logical groupings

The scanner skips common directories that don't contain feature code: `.git`, `.github`, `.help`, `.claude`, `.agents`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.tox`, `.venv`, `venv`, `env`, `node_modules`, `dist`, `build`, `.egg-info`, `htmlcov`, and `site`.

## Data structure

Each discovered feature becomes a `ProposedFeature` with:
- **name**: The feature identifier
- **description**: A brief explanation of what the feature does
- **files**: List of source files that implement the feature
- **tags**: Categories for grouping related features
- **confidence**: How certain the scanner is about the feature (defaults to 'medium')
- **reason**: Explanation for why this was identified as a feature

The `proposals_to_manifest()` function converts these proposals into a `FeatureManifest` that the documentation system can use.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
