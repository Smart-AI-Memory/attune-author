---
type: concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-04-12T04:19:20.863520+00:00
source_hash: 3fd0b912ad7c1588f2e6823e44da199dbb18303be141e9b9e8a7f5053f9157d2
status: generated
---

# Staleness And Maintenance

## How it works

Staleness and maintenance tracks when help templates become outdated and automatically regenerates them to stay in sync with source code changes.

The system works by computing SHA-256 hashes of each feature's source files and comparing them against stored hashes in the help templates. When `compute_source_hash()` detects a mismatch, the template is marked stale. The `check_staleness()` function scans all features and produces a `StalenessReport` showing how many templates are current versus stale.

For automated updates, `run_maintenance()` combines staleness detection with regeneration. It can operate on all features or a subset, with optional dry-run mode for testing. The `run_hook()` function provides a post-commit hook that only regenerates templates when their source files changed in the most recent commit, using `get_changed_files()` to minimize unnecessary work.

## Core data structures

**`FeatureStaleness`** — Tracks whether a single feature's help template is current or stale relative to its source files.

**`StalenessReport`** — Aggregates staleness across all checked features, providing counts through `stale_count()` and `current_count()` methods, plus a `stale_features()` list for identifying which ones need updates.

**`MaintenanceResult`** — Records the outcome of a maintenance run, including how many templates were found stale (`stale_count()`) and how many were actually regenerated (`regenerated_count()`).

## Integration points

Other parts of the codebase interact with staleness and maintenance through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `FeatureStaleness` | Staleness status for one feature. | `src/attune_author/staleness.py` |
| `StalenessReport` | Staleness report across all features. | `src/attune_author/staleness.py` |
| `MaintenanceResult` | Result of a help maintenance run. | `src/attune_author/maintenance.py` |
