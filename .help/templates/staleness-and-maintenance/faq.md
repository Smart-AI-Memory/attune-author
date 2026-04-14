---
type: faq
feature: staleness-and-maintenance
depth: faq
generated_at: 2026-04-14T16:11:29.761083+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness And Maintenance FAQ

## What is staleness detection?

Staleness detection identifies when your generated help templates are out of sync with their source code by comparing SHA-256 hashes of the source files.

## When should I check for stale templates?

Check for staleness when you've modified source code and want to know if the help templates need regeneration. You can run checks manually or set up the post-commit hook to check automatically after each commit.

## How do I check which templates are stale?

Use `check_staleness()` to get a report showing which features have outdated templates. The function compares stored hashes with current source file hashes and returns a `StalenessReport` with the results.

## What's the difference between checking staleness and running maintenance?

`check_staleness()` only reports which templates are stale, while `run_maintenance()` both checks for staleness and regenerates the stale templates automatically.

## How does the post-commit hook work?

The `run_hook()` function checks if any files changed in the most recent commit affect feature templates. If they do, it runs maintenance to regenerate the affected templates.

## What files does staleness checking examine?

The system examines all source files for a feature while excluding common cache and build directories like `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `node_modules`, and `.git`.

## Can I run maintenance without actually regenerating files?

Yes, use the `dry_run=True` parameter with `run_maintenance()` to see what would be regenerated without making any changes.

## How do I debug staleness issues?

Run the related tests first: `pytest -k "staleness-and-maintenance" -v`. If they pass but your code still fails, add a `logger.debug` statement at the suspected failure point and re-run with logging enabled.

For common failure modes, see the troubleshooting page for this feature.

## Where are the source files?

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
