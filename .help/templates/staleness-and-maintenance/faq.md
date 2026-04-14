---
type: faq
feature: staleness-and-maintenance
depth: faq
generated_at: 2026-04-14T14:06:37.158292+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance FAQ

## What is staleness and maintenance?

This feature detects when your help templates are out of sync with their source code and automatically regenerates the stale ones.

## When should I use it?

Use this feature when you need to keep your generated documentation current with code changes. It's essential for automated workflows like commit hooks that ensure documentation stays fresh.

## How do I check which templates are stale?

Use `check_staleness()` to get a report of which features have outdated templates. It compares SHA-256 hashes of source files against stored values to detect changes.

## How do I regenerate stale templates?

Call `run_maintenance()` to check staleness and regenerate any out-of-date templates in one operation. Set `dry_run=True` to see what would be regenerated without making changes.

## What's the difference between staleness checking and maintenance?

Staleness checking (`check_staleness()`) only reports which templates are out of date. Maintenance (`run_maintenance()`) goes further and actually regenerates the stale templates.

## Can I check staleness for specific features only?

Yes, pass a list of feature names to the `features` parameter in both `check_staleness()` and `run_maintenance()`. Without this parameter, all features are checked.

## How does the post-commit hook work?

The `run_hook()` function automatically runs maintenance after commits, but only if files changed in the latest commit. This prevents unnecessary regeneration when documentation files haven't changed.

## How do I debug staleness issues?

Run `pytest -k "staleness-and-maintenance" -v` first. If tests pass but you're still having issues, add `logger.debug` statements and enable logging to trace the hash computation and file matching logic.

## Where are the source files?

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
