---
type: warning
feature: bootstrap
depth: warning
generated_at: 2026-04-14T16:08:52.281340+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Bootstrap cautions

## What to watch for

The bootstrap scanner makes opinionated decisions about your project structure that can miss important features or misclassify existing code. Since it generates the initial manifest that guides all subsequent help generation, incorrect bootstrapping cascades through your entire documentation system.

## Risk areas

### Incomplete project discovery

`scan_project()` skips directories in `_SKIP_DIRS` and only recognizes entry points from `_ENTRY_POINT_NAMES`. If your project uses non-standard naming conventions or nested structures, the scanner will miss significant portions of your codebase.

**Risk:** Critical features remain undocumented because they weren't detected during the initial scan.

### False confidence in feature classification

The `ProposedFeature.confidence` field defaults to 'medium', but the scanner's heuristics may assign high confidence to incorrect classifications. A file named `config.py` gets tagged as configuration even if it's actually a module that processes configuration files.

**Risk:** Misclassified features receive inappropriate documentation templates, creating confusing or incorrect help content.

### Overwriting existing manifests

`proposals_to_manifest()` generates a new `FeatureManifest` without checking for existing documentation or manual overrides. Running bootstrap on a project with customized help content will discard your edits.

**Risk:** Manual documentation improvements are lost when re-running the bootstrap process.

## How to avoid problems

1. **Review proposals before accepting.** Always inspect the `ProposedFeature` list from `scan_project()` before calling `proposals_to_manifest()`. Verify that detected features match your project's actual structure.

2. **Customize scanner constants for your project.** If you use non-standard entry point names or directory structures, modify `_ENTRY_POINT_NAMES` and `_SKIP_DIRS` before scanning to improve detection accuracy.

3. **Back up existing manifests.** Before re-running bootstrap on a project with existing documentation, save your current manifest and help files. Bootstrap is designed for initial setup, not incremental updates.

4. **Validate confidence scores.** Don't trust the default 'medium' confidence rating. Manually review each proposed feature's `reason` field to understand why the scanner classified it that way.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
