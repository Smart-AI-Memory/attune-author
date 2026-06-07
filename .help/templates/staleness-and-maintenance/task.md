---
type: task
feature: staleness-and-maintenance
depth: task
generated_at: 2026-04-26T19:48:08.669237+00:00
source_hash: 196e1038a7194fe466fe8c96559cc4197bb18833f5afc123452ec132dd9007b6
status: generated
---

# Work with staleness and maintenance

Use staleness and maintenance when you need to detect outdated generated templates and regenerate them automatically to keep your help system current with source code changes.

## Prerequisites

- Access to the project source code
- Understanding of how templates are generated from source files

## Check for stale templates

1. **Import the maintenance module**
   ```python
   from attune_author.maintenance import run_maintenance
   ```

2. **Run staleness detection**
   ```python
   result = run_maintenance(
       help_dir="docs/help",
       project_root=".",
       dry_run=True  # Check only, don't regenerate
   )
   ```

3. **Review the staleness report**
   ```python
   print(f"Found {result.stale_count} stale templates")
   print(result.staleness)  # Detailed report
   ```

## Regenerate outdated templates

1. **Run maintenance with regeneration enabled**
   ```python
   result = run_maintenance(
       help_dir="docs/help",
       project_root=".",
       dry_run=False  # Actually regenerate
   )
   ```

2. **Target specific features** (optional)
   ```python
   result = run_maintenance(
       help_dir="docs/help",
       project_root=".",
       features=["authentication", "error-handling"]
   )
   ```

## Set up automatic maintenance

1. **Configure the post-commit hook**
   ```python
   from attune_author.maintenance import run_hook

   # In your .git/hooks/post-commit script
   result = run_hook(
       help_dir="docs/help",
       project_root="."
   )
   ```

2. **Handle hook results**
   ```python
   if result and result.stale_count > 0:
       print(f"Regenerated {result.regenerated_count} templates")
   ```

## Format status reports

1. **Generate a readable status report**
   ```python
   from attune_author.maintenance import format_status_report

   report = format_status_report(
       result.staleness,
       help_dir="docs/help"
   )
   print(report)
   ```

2. **Check what files changed recently**
   ```python
   from attune_author.maintenance import get_changed_files

   changed = get_changed_files(".")
   print(f"Changed files: {changed}")
   ```

## Verification

You've successfully set up staleness and maintenance when:

- `run_maintenance()` returns a `MaintenanceResult` with accurate stale counts
- Dry runs identify stale templates without modifying files
- Regeneration updates only the templates that need refreshing
- Status reports clearly show which templates were updated and why
