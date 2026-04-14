---
type: tip
feature: bootstrap
depth: tip
generated_at: 2026-04-14T16:09:40.153554+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Use the two-step bootstrap workflow

## Recommendation

Run `scan_project()` first to discover features, then `proposals_to_manifest()` to convert accepted proposals into a working manifest.

## Why

This separation lets you review and filter proposals before committing to a manifest structure, avoiding feature bloat in the initial setup.

## Tradeoff

You'll need to write code to handle the intermediate `ProposedFeature` objects, but this extra step prevents the bootstrap from making wrong assumptions about your project's intent.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
