---
type: concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-04-11T04:53:15.017467+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness And Maintenance

## How it works

Staleness detection identifies when generated help templates no longer match their source code by comparing SHA-256 hashes of feature source files against stored values in template frontmatter.

The system tracks staleness at two levels:

- **Individual features** — `FeatureStaleness` holds the status for a single feature
- **Project-wide reports** — `StalenessReport` aggregates staleness across all features, providing counts of stale vs current templates and listing which specific features need updates

Maintenance operations use this staleness data to selectively regenerate only the templates that have fallen out of sync. `MaintenanceResult` captures the outcome, tracking how many templates were stale and how many got regenerated.

## Detection workflow

The staleness check follows this sequence:

1. `compute_source_hash()` generates a SHA-256 hash from all source files belonging to a feature
2. `check_staleness()` compares these fresh hashes against the `source_hash` values stored in existing template frontmatter
3. Features with mismatched hashes are flagged as stale in the resulting `StalenessReport`

## Maintenance triggers

You can run maintenance in three ways:

- **Manual refresh** — Call `run_maintenance()` directly to check and regenerate templates for specified features or the entire project
- **Post-commit hooks** — `run_hook()` automatically triggers maintenance after commits that modify source files
- **Changed file detection** — `get_changed_files()` identifies which files were modified in the most recent commit to scope maintenance work

The `format_status_report()` function converts staleness data into human-readable status messages for display in logs or command output.
