---
type: reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-04-14T14:05:36.533470+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness and maintenance reference

## Classes

### FeatureStaleness fields

| Field | Type | Default |
|-------|------|---------|
| `feature` | `str` | — |
| `is_stale` | `bool` | — |
| `current_hash` | `str` | — |
| `stored_hash` | `str \| None` | — |
| `matched_files` | `list[str]` | `[]` |

### StalenessReport fields

| Field | Type | Default |
|-------|------|---------|
| `entries` | `list[FeatureStaleness]` | — |

### StalenessReport properties

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Count of stale features |
| `current_count` | `int` | Count of up-to-date features |
| `stale_features` | `list[str]` | Names of stale features |

### MaintenanceResult fields

| Field | Type | Default |
|-------|------|---------|
| `staleness` | `StalenessReport` | — |
| `regenerated` | `list[GenerationResult]` | `[]` |
| `skipped_manual` | `list[str]` | `[]` |
| `failed` | `list[str]` | `[]` |

### MaintenanceResult properties

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Number of stale features detected |
| `regenerated_count` | `int` | Number of features regenerated |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `compute_source_hash` | `feature: Feature, project_root: str \| Path` | `tuple[str, list[str]]` | Compute SHA-256 hash of a feature's source files |
| `check_staleness` | `manifest: FeatureManifest, help_dir: str \| Path, project_root: str \| Path, features: list[str] \| None = None` | `StalenessReport` | Check which features have stale help templates |
| `run_maintenance` | `help_dir: str \| Path, project_root: str \| Path, features: list[str] \| None = None, dry_run: bool = False` | `MaintenanceResult` | Run help maintenance — check staleness and regenerate |
| `get_changed_files` | `project_root: str \| Path` | `list[str]` | Get files changed in the most recent commit |
| `run_hook` | `help_dir: str \| Path, project_root: str \| Path` | `MaintenanceResult \| None` | Post-commit hook entry point |
| `format_status_report` | `report: StalenessReport, help_dir: str \| Path \| None = None` | `str` | Format a staleness report for display |

## Constants

| Constant | Value |
|----------|-------|
| `EXCLUDED_DIRS` | `{'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'node_modules', '.git'}` |
