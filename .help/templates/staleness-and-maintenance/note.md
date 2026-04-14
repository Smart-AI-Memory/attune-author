---
type: note
feature: staleness-and-maintenance
depth: note
generated_at: 2026-04-14T16:11:54.503497+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Note: staleness and maintenance

## Context

The staleness and maintenance system detects when generated help templates are out of date with their source files and automatically regenerates stale ones. This system powers both commit hooks and manual refresh workflows.

## How staleness detection works

The system tracks template freshness by computing SHA-256 hashes of a feature's source files and comparing them against stored hashes. When source files change, their hash changes, indicating the template needs regeneration.

Key components:

- `FeatureStaleness` — Represents staleness status for a single feature, including the current hash, stored hash, and list of matched source files
- `StalenessReport` — Aggregates staleness data across all features, with properties for counting stale vs. current features
- `compute_source_hash()` — Generates SHA-256 hashes from feature source files, excluding common cache directories like `__pycache__` and `.git`
- `check_staleness()` — Compares current hashes against stored ones to identify stale features

## Maintenance workflow

The maintenance system builds on staleness detection to automatically refresh outdated templates:

- `MaintenanceResult` — Captures the outcome of a maintenance run, tracking regenerated features, manual-only features that were skipped, and any failures
- `run_maintenance()` — Orchestrates the full process: check staleness, regenerate stale templates, and report results
- `run_hook()` — Entry point for post-commit hooks that automatically maintain templates after code changes
- `get_changed_files()` — Identifies files modified in the most recent commit to optimize maintenance runs

The system supports both comprehensive maintenance runs and targeted updates based on recent changes.

## Source files

- `src/attune_author/staleness.py` — Staleness detection and hashing
- `src/attune_author/maintenance.py` — Template regeneration and hook integration

**Tags:** `freshness`, `hashing`, `regeneration`
