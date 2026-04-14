---
type: note
feature: staleness-and-maintenance
depth: note
generated_at: 2026-04-14T14:06:59.962600+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Note: staleness and maintenance

## What staleness detection does

The staleness detection system tracks when feature source code changes make help templates outdated. It computes SHA-256 hashes of each feature's source files and compares them against stored hashes to identify which templates need regeneration.

## Core data structures

The system uses three main classes:

**`FeatureStaleness`** represents the staleness state for a single feature. It stores the feature name, staleness flag, current source hash, previously stored hash, and list of matched source files.

**`StalenessReport`** aggregates staleness data across all features. It provides counts of stale and current features, plus a list of stale feature names.

**`MaintenanceResult`** captures the outcome of a maintenance run, including the staleness report, successfully regenerated templates, manually-maintained templates that were skipped, and any failures.

## Key functions

**Staleness checking:** `compute_source_hash()` generates hashes for a feature's source files, while `check_staleness()` compares current hashes against stored ones to build a staleness report.

**Maintenance operations:** `run_maintenance()` performs the full cycle of checking staleness and regenerating outdated templates. It supports dry-run mode and can target specific features.

**Git integration:** `get_changed_files()` identifies files modified in the latest commit, and `run_hook()` serves as the entry point for post-commit hooks that trigger maintenance automatically.

The system excludes common cache and build directories (like `__pycache__` and `.git`) when computing source hashes to focus on meaningful code changes.
