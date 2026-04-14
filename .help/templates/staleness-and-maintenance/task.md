---
type: task
feature: staleness-and-maintenance
depth: task
generated_at: 2026-04-14T16:10:20.706262+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Work with staleness and maintenance

Use staleness and maintenance when you need to keep help templates synchronized with source code changes or set up automated regeneration workflows.

## Prerequisites

- Access to the project source code
- Write permissions to the help directory
- Understanding of your project's feature structure

## Check template staleness

1. **Import the staleness checker:**
   ```python
   from attune_author.staleness import check_staleness
   from attune_author.manifest import load_manifest
   ```

2. **Load your feature manifest:**
   ```python
   manifest = load_manifest("path/to/help")
   ```

3. **Run the staleness check:**
   ```python
   report = check_staleness(manifest, "path/to/help", "path/to/project")
   ```

4. **Review the results:**
   ```python
   print(f"Stale features: {report.stale_count}")
   print(f"Up-to-date features: {report.current_count}")
   for feature in report.stale_features:
       print(f"  - {feature}")
   ```

## Regenerate stale templates

1. **Run maintenance to update templates:**
   ```python
   from attune_author.maintenance import run_maintenance

   result = run_maintenance("path/to/help", "path/to/project")
   ```

2. **Check for specific features only:**
   ```python
   result = run_maintenance(
       "path/to/help",
       "path/to/project",
       features=["feature1", "feature2"]
   )
   ```

3. **Preview changes without applying them:**
   ```python
   result = run_maintenance(
       "path/to/help",
       "path/to/project",
       dry_run=True
   )
   ```

## Set up automated maintenance

1. **Configure a post-commit hook:**
   ```python
   from attune_author.maintenance import run_hook

   # In your git hook script
   result = run_hook("path/to/help", "path/to/project")
   if result and result.regenerated_count > 0:
       print(f"Regenerated {result.regenerated_count} templates")
   ```

2. **Add the hook to your git workflow:**
   Create `.git/hooks/post-commit` with execute permissions:
   ```bash
   #!/bin/bash
   python -c "
   from attune_author.maintenance import run_hook
   run_hook('docs/help', '.')
   "
   ```

## Verify success

Your maintenance workflow is working correctly when:

- `check_staleness()` returns a report with `stale_count` of 0 for up-to-date features
- `run_maintenance()` completes without entries in the `failed` list
- Template files show recent modification timestamps after regeneration
- The post-commit hook runs without errors and updates templates when source files change

## Key files

- `src/attune_author/staleness.py` - Hash computation and staleness detection
- `src/attune_author/maintenance.py` - Template regeneration and automation
