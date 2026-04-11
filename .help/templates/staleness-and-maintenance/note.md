---
type: note
feature: staleness-and-maintenance
depth: note
generated_at: 2026-04-11T04:54:55.359328+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Note: staleness and maintenance

## Context

Help templates become stale when their source files change. This feature detects staleness by comparing SHA-256 hashes of source files against stored hashes in template frontmatter, then regenerates outdated templates automatically.

## Content

The staleness detection works through three data classes that track state:

- `FeatureStaleness` — Staleness status for a single feature
- `StalenessReport` — Aggregated staleness data across all features, with methods to count stale vs. current features
- `MaintenanceResult` — Results from a maintenance run, tracking how many templates were stale and how many got regenerated

Five functions handle the detection and regeneration workflow:

- `compute_source_hash()` — Generates SHA-256 hashes from a feature's source files
- `check_staleness()` — Compares stored hashes against current source to identify stale templates
- `run_maintenance()` — Orchestrates the full check-and-regenerate cycle, with optional dry-run mode
- `get_changed_files()` — Retrieves files modified in the most recent Git commit
- `run_hook()` — Entry point for post-commit hooks that trigger maintenance automatically

The classes and functions work together — `check_staleness()` returns a `StalenessReport`, while `run_maintenance()` returns a `MaintenanceResult` after processing any stale features found.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
