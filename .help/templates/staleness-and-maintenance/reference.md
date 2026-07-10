---
type: reference
name: staleness-and-maintenance-reference
feature: staleness-and-maintenance
depth: reference
generated_at: 2026-07-10T13:08:07.309914+00:00
source_hash: f70ee7dc8566b26c31c6469a302951de9b7e530870798083457598b8f84d96d6
status: generated
scaffold_hash: f1a8f510d67d3cb758568efd61ee786fe8c32dc18b84f59ac7a458c698175ded
---

# Staleness and maintenance reference

Detect when generated help templates and project docs are out of date with their source files, and regenerate the stale ones — either on demand or from a post-commit hook.

## Classes

| Class | Description | File |
|-------|-------------|------|
| `MaintenanceResult` | Result of a help maintenance run. | `src/attune_author/maintenance.py` |
| `FeatureStaleness` | Staleness status for one feature's `.help/` templates. | `src/attune_author/staleness.py` |
| `DocStaleness` | Staleness status for one project doc file in `docs/`. | `src/attune_author/staleness.py` |
| `StalenessReport` | Combined staleness report across help templates and project docs. | `src/attune_author/staleness.py` |

### MaintenanceResult

Fields:

| Field | Type | Default |
|-------|------|---------|
| `staleness` | `StalenessReport` | — |
| `regenerated` | `list[GenerationResult]` | `field(default_factory=list)` |
| `skipped_manual` | `list[str]` | `field(default_factory=list)` |
| `failed` | `list[str]` | `field(default_factory=list)` |

Properties:

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Number of stale features detected. |
| `regenerated_count` | `int` | Number of features regenerated. |

### FeatureStaleness

Fields:

| Field | Type | Default |
|-------|------|---------|
| `feature` | `str` | — |
| `is_stale` | `bool` | — |
| `current_hash` | `str` | — |
| `stored_hash` | `str \| None` | — |
| `matched_files` | `list[str]` | `field(default_factory=list)` |

### DocStaleness

Fields:

| Field | Type | Default |
|-------|------|---------|
| `feature` | `str` | — |
| `doc_path` | `str` | — |
| `kind` | `str` | — |
| `is_stale` | `bool` | — |
| `missing` | `bool` | — |
| `current_hash` | `str` | — |
| `stored_hash` | `str \| None` | `None` |

### StalenessReport

Fields:

| Field | Type | Default |
|-------|------|---------|
| `help_entries` | `list[FeatureStaleness]` | `field(default_factory=list)` |
| `doc_entries` | `list[DocStaleness]` | `field(default_factory=list)` |
| `manual_features` | `list[str]` | `field(default_factory=list)` |

Properties:

| Property | Type | Description |
|----------|------|-------------|
| `stale_count` | `int` | Total stale items across both sections. |
| `current_count` | `int` | Total up-to-date items across both sections. |
| `stale_features` | `list[str]` | Names of features with stale help templates. |
| `stale_docs` | `list[DocStaleness]` | Doc entries that are stale or missing. |

## Functions

| Function | Parameters | Returns | Description | File |
|----------|------------|---------|-------------|------|
| `run_maintenance` | `help_dir: str \| Path, project_root: str \| Path, features: list[str] \| None = None, dry_run: bool = False` | `MaintenanceResult` | Checks staleness and regenerates stale help templates. | `src/attune_author/maintenance.py` |
| `get_changed_files` | `project_root: str \| Path` | `list[str]` | Returns the files changed in the most recent commit. | `src/attune_author/maintenance.py` |
| `run_hook` | `help_dir: str \| Path, project_root: str \| Path` | `MaintenanceResult \| None` | Post-commit hook entry point. | `src/attune_author/maintenance.py` |
| `format_status_report` | `report: StalenessReport, help_dir: str \| Path \| None = None` | `str` | Formats a staleness report for display. | `src/attune_author/maintenance.py` |
| `compute_semantic_hash` | `feature: Feature, project_root: str \| Path, extractor: object \| None = None` | `tuple[str, list[str]]` | Computes a semantic SHA-256 hash of a feature's Python source files. | `src/attune_author/staleness.py` |
| `compute_source_hash` | `feature: Feature, project_root: str \| Path` | `tuple[str, list[str]]` | Computes the SHA-256 hash of a feature's source files. | `src/attune_author/staleness.py` |
| `parse_doc_footer` | `text: str` | `dict[str, str]` | Parses an attune-generated HTML comment footer. | `src/attune_author/staleness.py` |
| `build_doc_footer` | `source_hash: str, feature: str, kind: str, generated_at: str` | `str` | Builds an attune-generated HTML comment footer line. | `src/attune_author/staleness.py` |
| `check_staleness` | `manifest: FeatureManifest, help_dir: str \| Path, project_root: str \| Path, features: list[str] \| None = None` | `StalenessReport` | Checks staleness across help templates and project docs. | `src/attune_author/staleness.py` |
| `check_workspace_staleness` | `workspace: str \| Path, features: list[str] \| None = None` | `StalenessReport` | Checks staleness for a workspace using the conventional `.help/` layout. | `src/attune_author/staleness.py` |

## Constants

| Constant | Values | Description |
|----------|--------|-------------|
| `_EXCLUDED_DIRS` | `{'__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'node_modules', '.git'}` | Directories skipped when scanning a feature's source files for hashing. |

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

## Tags

`freshness`, `hashing`, `regeneration`
