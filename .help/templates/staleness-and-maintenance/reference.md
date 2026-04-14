---
type: reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-04-14T16:10:33.520693+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness and maintenance reference

Detect when help templates are out of sync with source code and automatically regenerate them.

## Classes

### FeatureStaleness

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `feature` | `str` |  | Name of the feature being checked |
| `is_stale` | `bool` |  | Whether the help template is out of sync with source |
| `current_hash` | `str` |  | SHA-256 hash of current source files |
| `stored_hash` | `str \| None` |  | Hash stored in the template's frontmatter |
| `matched_files` | `list[str]` | `field(default_factory=list)` | Source files used to compute the hash |

### StalenessReport

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `entries` | `list[FeatureStaleness]` |  | Staleness status for each checked feature |

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Count of stale features |
| `current_count` | `int` | Count of up-to-date features |
| `stale_features` | `list[str]` | Names of stale features |

### MaintenanceResult

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `staleness` | `StalenessReport` |  | Staleness report for all checked features |
| `regenerated` | `list[GenerationResult]` | `field(default_factory=list)` | Successfully regenerated templates |
| `skipped_manual` | `list[str]` | `field(default_factory=list)` | Features skipped due to manual status |
| `failed` | `list[str]` | `field(default_factory=list)` | Features that failed to regenerate |

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

| Constant | Values | Description |
|----------|--------|-------------|
| `_EXCLUDED_DIRS` | `{'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'node_modules', '.git'}` | Directories excluded from source file scanning |
