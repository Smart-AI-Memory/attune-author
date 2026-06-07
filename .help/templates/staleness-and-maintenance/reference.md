---
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-06-06T23:19:48.582350+00:00
source_hash: a32e9d9904602f0f282f0bf02f119e350efd6c8b4ecb73c04564917b6ae65f69
status: generated
---

# Staleness And Maintenance reference

## Classes

| Class | Description | File |
|-------|-------------|------|
| `FeatureStaleness` | Staleness status for one feature's ``.help/`` templates. | `src/attune_author/staleness.py` |
| `DocStaleness` | Staleness status for one project doc file in ``docs/``. | `src/attune_author/staleness.py` |
| `StalenessReport` | Combined staleness report across help templates and project docs. | `src/attune_author/staleness.py` |
| `MaintenanceResult` | Result of a help maintenance run. | `src/attune_author/maintenance.py` |

## Functions

| Function | Description | File |
|----------|-------------|------|
| `compute_semantic_hash()` | Compute a semantic SHA-256 hash of a feature's Python source files. | `src/attune_author/staleness.py` |
| `compute_source_hash()` | Compute SHA-256 hash of a feature's source files. | `src/attune_author/staleness.py` |
| `parse_doc_footer()` | Parse an attune-generated HTML comment footer. | `src/attune_author/staleness.py` |
| `build_doc_footer()` | Build an attune-generated HTML comment footer line. | `src/attune_author/staleness.py` |
| `check_staleness()` | Check staleness across help templates and project docs. | `src/attune_author/staleness.py` |
| `check_workspace_staleness()` | Check staleness for a workspace using the conventional ``.help/`` layout. | `src/attune_author/staleness.py` |
| `run_maintenance()` | Run help maintenance — check staleness and regenerate. | `src/attune_author/maintenance.py` |
| `get_changed_files()` | Get files changed in the most recent commit. | `src/attune_author/maintenance.py` |
| `run_hook()` | Post-commit hook entry point. | `src/attune_author/maintenance.py` |
| `format_status_report()` | Format a staleness report for display. | `src/attune_author/maintenance.py` |


## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

## Tags

`freshness`, `hashing`, `regeneration`
