---
type: note
feature: bootstrap
depth: note
generated_at: 2026-04-11T04:52:54.090042+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Note: bootstrap

## Context

The bootstrap feature scans Python projects to automatically propose an initial feature manifest. It analyzes directory structure and package layout to suggest logical feature boundaries, reducing the manual work needed to set up attune-author for a new project.

## Content

Bootstrap provides a two-step workflow for generating feature manifests:

1. **Project scanning** — `scan_project()` traverses your project directory and returns a list of `ProposedFeature` objects based on discovered packages, modules, and directory patterns.

2. **Manifest generation** — `proposals_to_manifest()` takes the proposed features (after you review and filter them) and converts them into a `FeatureManifest` that attune-author can use.

The `ProposedFeature` class represents a potential feature discovered during scanning. Each instance contains information about the feature's scope, suggested name, and the files or directories it would encompass.

This approach lets you quickly bootstrap a new project while maintaining control over the final feature boundaries through the proposal review step.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
