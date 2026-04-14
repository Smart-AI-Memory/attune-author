---
type: concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-04-14T14:05:15.488389+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance

Staleness and maintenance automatically detects when generated help templates are out of sync with their source code and regenerates outdated documentation.

## How it works

The system tracks changes by computing SHA-256 hashes of each feature's source files and comparing them against stored values. When source code changes, the corresponding help templates become stale and need regeneration.

The staleness detection process examines specific file patterns for each feature while excluding common build artifacts like `__pycache__`, `.mypy_cache`, and `.git` directories. It returns a detailed report showing which features are current and which need updates.

For maintenance operations, you can run checks manually or automatically via commit hooks. The `run_hook` function provides a post-commit entry point that only regenerates templates when relevant files have changed in the most recent commit.

## Core data structures

**`FeatureStaleness`** captures the staleness status for a single feature, including the current source hash, previously stored hash, and list of files that contributed to the hash calculation.

**`StalenessReport`** aggregates staleness information across all features, providing counts of stale versus current features and listing which specific features need updates.

**`MaintenanceResult`** records the outcome of a maintenance run, tracking which features were regenerated successfully, which were skipped due to manual status, and which failed during regeneration.

## Integration points

| Interface | Purpose | File |
|-----------|---------|------|
| `FeatureStaleness` | Staleness status for one feature. | `src/attune_author/staleness.py` |
| `StalenessReport` | Staleness report across all features. | `src/attune_author/staleness.py` |
| `MaintenanceResult` | Result of a help maintenance run. | `src/attune_author/maintenance.py` |
