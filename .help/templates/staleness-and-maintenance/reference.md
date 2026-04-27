---
type: reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-04-26T19:48:20.345159+00:00
source_hash: 196e1038a7194fe466fe8c96559cc4197bb18833f5afc123452ec132dd9007b6
status: generated
---

# Staleness and maintenance reference

Detect outdated help templates and regenerate them automatically. Check which templates need updating based on source code changes and run maintenance operations to keep documentation fresh.

## Classes

| Class | Description |
|-------|-------------|
| `MaintenanceResult` | Result of a help maintenance run |

### MaintenanceResult fields

| Field | Type | Default |
|-------|------|---------|
| `staleness` | `StalenessReport` | |
| `regenerated` | `list[GenerationResult]` | `field(default_factory=list)` |
| `skipped_manual` | `list[str]` | `field(default_factory=list)` |
| `failed` | `list[str]` | `field(default_factory=list)` |

### MaintenanceResult properties

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Number of stale features detected |
| `regenerated_count` | `int` | Number of features regenerated |

## Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `run_maintenance` | `help_dir: str \| Path, project_root: str \| Path, features: list[str] \| None = None, dry_run: bool = False` | `MaintenanceResult` | Run help maintenance — check staleness and regenerate |
| `get_changed_files` | `project_root: str \| Path` | `list[str]` | Get files changed in the most recent commit |
| `run_hook` | `help_dir: str \| Path, project_root: str \| Path` | `MaintenanceResult \| None` | Post-commit hook entry point |
| `format_status_report` | `report: StalenessReport, help_dir: str \| Path \| None = None` | `str` | Format a staleness report for display |

## Constants

| Constant | Values |
|----------|--------|
| `__all__` | `['DocStaleness', 'FeatureStaleness', 'StalenessReport', '_read_frontmatter_value', 'build_doc_footer', 'check_staleness', 'compute_source_hash', 'parse_doc_footer']` |
