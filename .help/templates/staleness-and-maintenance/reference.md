---
type: reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-04-12T04:19:41.029381+00:00
source_hash: 3fd0b912ad7c1588f2e6823e44da199dbb18303be141e9b9e8a7f5053f9157d2
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
| `stale_count()` | `int` | Number of stale features found |
| `regenerated_count()` | `int` | Number of features regenerated |

## Functions

| Function | Description |
|----------|-------------|
| `compute_source_hash()` | Compute SHA-256 hash of a feature's source files |
| `check_staleness()` | Check which features have stale help templates |
| `run_maintenance()` | Run help maintenance — check staleness and regenerate |
| `get_changed_files()` | Get files changed in the most recent commit |
| `run_hook()` | Post-commit hook entry point |
| `format_status_report()` | Format a staleness report for display |

### Function signatures

```python
compute_source_hash(feature: Feature, project_root: str | Path) -> tuple[str, list[str]]
```

```python
check_staleness(manifest: FeatureManifest, help_dir: str | Path,
               project_root: str | Path, features: list[str] | None = None) -> StalenessReport
```

```python
run_maintenance(help_dir: str | Path, project_root: str | Path,
               features: list[str] | None = None, dry_run: bool = False) -> MaintenanceResult
```

```python
get_changed_files(project_root: str | Path) -> list[str]
```

```python
run_hook(help_dir: str | Path, project_root: str | Path) -> MaintenanceResult | None
```

```python
format_status_report(report: StalenessReport, help_dir: str | Path | None = None) -> str
```

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

## Tags

`freshness`, `hashing`, `regeneration`
