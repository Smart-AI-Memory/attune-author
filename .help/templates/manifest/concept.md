---
type: concept
feature: manifest
depth: concept
generated_at: 2026-04-26T19:47:27.049260+00:00
source_hash: 83a32541b2c8d0a608f767253efe855779cf22ea2a49e097f20091f1c34012c2
status: generated
---

# Manifest

## What

The manifest is a centralized registry that maps your project's features to their help content. It lives in `.help/features.yaml` and tells the attune-help engine which features exist, how to identify source files that belong to each feature, and where to find their documentation templates.

## Why

Without a manifest, the help system would have to guess which files relate to which features by scanning your entire codebase on every query. The manifest eliminates this overhead by providing a definitive mapping. It also lets you control feature boundaries — deciding that "authentication" includes both `auth.py` and `session.py`, or that "database" covers everything in the `models/` directory.

## Structure and components

The manifest contains three main elements:

**Feature definitions** — Each feature has a name (like `authentication` or `task-runner`) and file patterns that identify which source files belong to it. The engine uses these patterns to match code changes to the right documentation.

**Version tracking** — The manifest includes a version field that the engine checks to ensure compatibility between your project's manifest format and the help system's expectations.

**Name validation** — Feature names must follow specific rules (alphanumeric, hyphens, and underscores only) to work correctly with the template naming system and cross-linking engine.

## File matching and topic resolution

When you ask about a feature, the engine uses the manifest to find relevant source files, then looks for templates that cover that feature. The `match_files_to_features` function takes a list of file paths and returns which features they belong to. The `resolve_topic` function does the reverse — given a feature name, it finds the appropriate help content.

This two-way mapping ensures that whether you start from code or from a question, the engine can connect you to the right information.
