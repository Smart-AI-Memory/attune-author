---
type: note
feature: bootstrap
depth: note
generated_at: 2026-04-14T14:04:52.652295+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Note: bootstrap

## Context

The bootstrap feature automatically discovers project structure and generates an initial feature manifest. It scans directories and files to identify potential features based on common Python project patterns.

## Content

Bootstrap uses a two-step process: scanning and manifest generation. The `scan_project()` function walks the project directory, skipping common non-source directories like `.git`, `__pycache__`, and `node_modules`. It identifies potential features by recognizing entry point files (`main.py`, `app.py`, `cli.py`, etc.) and configuration patterns (`config`, `settings`, `conf`).

Each discovered feature becomes a `ProposedFeature` with a name, description, associated files, tags, and confidence level. The scanner assigns confidence ratings based on how clearly it can identify the feature's purpose from file names and directory structure.

The `proposals_to_manifest()` function converts the list of proposed features into a `FeatureManifest` that can be saved as the project's initial documentation structure.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
