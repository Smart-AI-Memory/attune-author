---
type: concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-04-14T16:10:08.341587+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance

Staleness and maintenance automatically detects when help templates are outdated and regenerates them to keep documentation in sync with source code changes.

## How detection works

The system uses SHA-256 hashing to compare your current source files against the stored hash from when templates were last generated. When you modify source code that affects a feature's documentation, the system marks that feature's templates as stale.

The detection process examines all source files for each feature, excluding common build artifacts like `__pycache__`, `.mypy_cache`, and `node_modules`. For example, if you update a function signature in your feature's main module, `compute_source_hash()` will generate a new hash that doesn't match the stored value.

## Core data structures

**`FeatureStaleness`** tracks the staleness status for individual features. It stores the current hash of source files, the previously stored hash, whether the feature is stale, and which specific files were included in the hash calculation.

**`StalenessReport`** aggregates staleness information across all features in your project. It provides counts of stale versus current features and lists the names of features that need regeneration.

**`MaintenanceResult`** captures the outcome of a maintenance run, including which features were detected as stale, which were successfully regenerated, which were skipped due to manual edits, and which failed during regeneration.

## Maintenance workflows

You can run maintenance in two ways: manually through `run_maintenance()` or automatically via the post-commit hook with `run_hook()`. The manual approach lets you specify which features to check and supports dry-run mode to preview changes without making them.

The post-commit hook automatically triggers after commits, using `get_changed_files()` to focus only on features whose source files were modified in the most recent commit. This targeted approach keeps the hook fast while ensuring affected documentation stays current.
