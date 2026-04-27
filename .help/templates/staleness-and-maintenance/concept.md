---
type: concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-04-26T19:47:57.095143+00:00
source_hash: 196e1038a7194fe466fe8c96559cc4197bb18833f5afc123452ec132dd9007b6
status: generated
---

# Staleness And Maintenance

## How it works

Staleness detection identifies when generated help templates are out of sync with their source code. When you modify functions, classes, or files that generated templates reference, those templates become stale and need regeneration to reflect current behavior.

The system tracks this through source hashes — cryptographic fingerprints of the code that generated each template. When source files change, their hashes change, marking dependent templates as stale.

## Core components

**MaintenanceResult** captures what happened during a maintenance run. It tracks which features were stale, which got regenerated successfully, which were skipped because they require manual updates, and which failed during regeneration.

**Staleness detection** compares current source hashes against the hashes stored in template frontmatter. Templates with mismatched hashes are marked stale and queued for regeneration.

**Automated maintenance** runs either manually through `run_maintenance()` or automatically via the post-commit hook. The hook examines recent git changes and regenerates only templates affected by those changes.

## When staleness matters

Templates become stale in three scenarios:

1. **Function signatures change** — adding parameters, changing return types, or modifying docstrings
2. **Class structure evolves** — new methods, field additions, or inheritance changes
3. **Module organization shifts** — moving files, renaming modules, or changing import paths

The maintenance system prevents documentation drift by catching these changes before templates mislead users.

## Hook integration

The post-commit hook automatically runs maintenance after each commit. It examines `get_changed_files()` to identify what changed, then regenerates only the templates that depend on those files. This keeps help content fresh without manual intervention.

For manual maintenance, `run_maintenance()` can target specific features or scan the entire help directory. The `dry_run` option shows what would be regenerated without making changes.
