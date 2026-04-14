---
type: comparison
feature: bootstrap
depth: comparison
generated_at: 2026-04-14T16:09:53.912253+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap vs manual manifest creation

## Context

The bootstrap feature automatically scans your project structure to generate an initial features manifest. You can alternatively create manifests by hand or use other project analysis tools.

## Feature comparison

| Aspect | Bootstrap scanning | Manual manifest creation |
|--------|-------------------|--------------------------|
| **Speed** | Seconds for most projects | Minutes to hours depending on size |
| **Accuracy** | Medium confidence by default, may miss domain-specific features | High accuracy for features you understand |
| **Coverage** | Finds standard patterns (entry points, configs, common directories) | Only includes what you explicitly add |
| **Customization** | Limited to built-in heuristics and confidence levels | Full control over feature definitions |
| **Learning curve** | None — just run `scan_project()` | Requires understanding manifest format |
| **Maintenance** | Proposals become stale as code evolves | You maintain accuracy through manual updates |

## Use bootstrap when

- **Starting fresh**: You need an initial manifest for a new or undocumented project
- **Quick discovery**: You want to identify obvious features without deep analysis
- **Standard layouts**: Your project follows common Python conventions (has `main.py`, `config/` directories, etc.)
- **Exploration**: You're unsure what features exist and want suggestions to refine

The `scan_project()` function excels at finding entry points like `main.py` and `server.py`, configuration directories matching patterns like `config` and `settings`, and skipping noise directories like `.git` and `__pycache__`.

## Use manual creation when

- **Domain expertise**: You understand your project's architecture better than heuristics can
- **Precision matters**: You need specific feature boundaries that don't match file system layout
- **Complex projects**: Your codebase has unusual organization or mixed languages
- **Integration work**: You're incorporating the manifest into existing documentation or tooling workflows

## Converting proposals to manifests

Bootstrap doesn't make decisions for you — it creates `ProposedFeature` objects that you review and accept. Use `proposals_to_manifest()` to convert the proposals you want into a working `FeatureManifest`.

This two-step process lets you catch scanning errors and add context that file system analysis can't provide.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
