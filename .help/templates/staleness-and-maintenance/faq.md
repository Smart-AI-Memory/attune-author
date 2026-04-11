---
type: faq
feature: staleness-and-maintenance
depth: faq
generated_at: 2026-04-11T04:54:30.680846+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Staleness And Maintenance FAQ

## What is staleness detection?

Staleness detection checks if your generated help templates are out of sync with their source code by comparing SHA-256 hashes of the source files.

## When do templates become stale?

Templates become stale when you modify source files but don't regenerate the corresponding help templates. The system detects this by comparing the current source hash with the hash stored in each template's frontmatter.

## How do I check which templates are stale?

Use `check_staleness()` to get a report showing which features have outdated templates. The `StalenessReport` tells you the count of stale features and lists them by name.

## How do I fix stale templates?

Run `run_maintenance()` to automatically regenerate stale templates. Set `dry_run=True` to see what would be regenerated without making changes.

## Can I automate this with Git hooks?

Yes. Use `run_hook()` as a post-commit hook entry point. It automatically checks for staleness and regenerates templates when source files change in a commit.

## Which files does staleness tracking monitor?

The system monitors all source files that contribute to a feature's help template, as determined by `compute_source_hash()`. This includes the feature's main source files and any dependencies.

## How do I see a formatted staleness report?

Use `format_status_report()` to get a human-readable summary of which templates are stale and which are current.

## How do I debug staleness issues?

Run `pytest -k "staleness-and-maintenance" -v` first. If tests pass but you're still having issues, add debug logging at the point where staleness detection or maintenance fails.

## Where are the source files?

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
