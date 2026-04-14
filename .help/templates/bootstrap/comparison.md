---
type: comparison
feature: bootstrap
depth: comparison
generated_at: 2026-04-14T14:04:59.815483+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap vs manual manifest creation

## Context

When starting a new project with attune-author, you need a feature manifest that describes your codebase structure. You can either use the bootstrap scanner to generate initial proposals automatically, or create the manifest file manually from scratch.

## Feature comparison

| Aspect | Bootstrap scanner | Manual creation |
|--------|------------------|-----------------|
| **Setup time** | ~30 seconds to scan and review | 15-45 minutes depending on project size |
| **Accuracy** | Finds obvious patterns (entry points, configs) but may miss domain-specific features | Perfect accuracy for your specific use case |
| **Coverage** | Scans standard directories, skips build artifacts and version control | You control exactly what gets included |
| **Maintenance** | Re-run when project structure changes significantly | Update manifest as you add features |
| **Learning curve** | Immediate results, inspect output to understand manifest format | Requires understanding manifest schema upfront |

## Use bootstrap when...

- You're starting fresh with an existing codebase
- Your project follows standard Python conventions (has `main.py`, `config.py`, typical directory structure)
- You want to understand what a feature manifest looks like before writing your own
- You're prototyping or exploring the attune-author workflow

The scanner recognizes common entry points like `main.py`, `app.py`, and `cli.py`, plus configuration patterns containing "config", "settings", or "conf". It automatically skips build directories, caches, and version control folders.

## Use manual creation when...

- Your project has unconventional structure that automated scanning won't understand
- You need fine-grained control over feature definitions and confidence levels
- You're working with a domain-specific codebase (embedded systems, data science notebooks, etc.)
- You want to define features that don't correspond to file boundaries

Manual creation gives you complete control over the `ProposedFeature` fields: name, description, associated files, tags, confidence level, and reasoning.

## Recommended workflow

Start with bootstrap scanning to get a foundation, then manually refine the results:

1. Run `scan_project()` on your project root
2. Review the generated `ProposedFeature` objects for accuracy
3. Edit confidence levels, descriptions, and tags as needed
4. Use `proposals_to_manifest()` to generate your initial manifest
5. Maintain the manifest manually as your project evolves

This hybrid approach gets you started quickly while ensuring the final result matches your project's reality.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
