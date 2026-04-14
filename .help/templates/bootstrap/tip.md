---
type: tip
feature: bootstrap
depth: tip
generated_at: 2026-04-14T14:04:47.063761+00:00
source_hash: 747d4d8b3e41bb5a6d7a534fb1402fcfcda15486e7b1994427f88a2f71907ebf
status: generated
---

# Start with scan_project() for automated feature discovery

## Recommendation

Use `scan_project()` to generate your initial feature manifest instead of writing one from scratch.

## Why

The scanner recognizes common patterns like entry points (`main.py`, `app.py`) and configuration files, saving you from manually cataloging obvious features and reducing the chance of missing something important.

## Tradeoff

Auto-generated proposals have generic descriptions and may suggest irrelevant features for unusual project structures—you'll need to review and refine the `ProposedFeature` objects before converting them to your final manifest with `proposals_to_manifest()`.
