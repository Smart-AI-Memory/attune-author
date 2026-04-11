---
type: comparison
feature: staleness-and-maintenance
depth: comparison
generated_at: 2026-04-11T04:55:03.768171+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness detection vs manual help maintenance

## Context

You need to keep generated help templates in sync with source code changes. You can either detect staleness automatically and regenerate templates on demand, or manually regenerate templates whenever you remember to do so.

## Feature comparison

| Aspect | Automatic staleness detection | Manual regeneration |
|--------|------------------------------|-------------------|
| **Accuracy** | SHA-256 hashing catches all source changes | Relies on remembering which files changed |
| **Integration** | Post-commit hooks run automatically | Requires manual command execution |
| **Feedback speed** | Immediate detection via `check_staleness()` | Only discovered when templates are visibly wrong |
| **Maintenance overhead** | Initial setup, then zero ongoing work | Constant vigilance required |
| **Selective updates** | Can target specific features or changed files | All-or-nothing regeneration |
| **Safety** | Dry-run mode prevents accidental overwrites | Easy to lose manual edits |

## Staleness detection workflow

The automatic approach uses three main operations:

- **Detection**: `check_staleness()` compares current source hashes against stored values in template frontmatter
- **Selective maintenance**: `run_maintenance()` regenerates only stale templates, with optional dry-run mode
- **Hook integration**: `run_hook()` automatically runs after commits, processing only files that changed

## Manual maintenance workflow

Without staleness detection, you must:

- Remember which source files you modified
- Manually run regeneration commands
- Hope you didn't miss any affected templates
- Manually verify the results look correct

## Use automatic staleness detection when...

- You want zero-maintenance template freshness
- Multiple people contribute to the codebase
- You integrate help generation into CI/CD pipelines
- You need to track which specific features are out of date

**Automatic detection is the recommended approach** — it eliminates a entire class of human error and provides better development experience with minimal setup cost.

## Use manual maintenance when...

- You're doing one-off template generation
- Your source files change infrequently (less than weekly)
- You need custom regeneration logic that the maintenance system doesn't support

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
