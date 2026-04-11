---
type: reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-04-11T04:53:34.361943+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness and maintenance reference

## Classes

| Class | Description |
|-------|-------------|
| `FeatureStaleness` | Staleness status for one feature |
| `StalenessReport` | Staleness report across all features |
| `MaintenanceResult` | Result of a help maintenance run |

### StalenessReport methods

| Method | Return type | Description |
|--------|-------------|-------------|
| `stale_count()` | `int` | Number of features with stale help templates |
| `current_count()` | `int` | Number of features with current help templates |
| `stale_features()` | `list[str]` | Names of features with stale help templates |

### MaintenanceResult methods

| Method | Return type | Description |
|--------|-------------|-------------|
| `stale_count()` | `int` | Number of features that were stale before maintenance |
| `regenerated_count()` | `int` | Number of help templates that were regenerated |

## Functions

| Function | Description |
|----------|-------------|
| `compute_source_hash(feature, project_root)` | Compute SHA-256 hash of a feature's source files |
| `check_staleness(manifest, help_dir, project_root, features=None)` | Check which features have stale help templates |
| `run_maintenance(help_dir, project_root, features=None, dry_run=False)` | Run help maintenance — check staleness and regenerate |
| `get_changed_files(project_root)` | Get files changed in the most recent commit |
| `run_hook(help_dir, project_root)` | Post-commit hook entry point |
| `format_status_report(report, help_dir=None)` | Format a staleness report for display |
