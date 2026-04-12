---
type: task
feature: staleness-and-maintenance
depth: task
generated_at: 2026-04-12T04:19:29.971125+00:00
source_hash: 3fd0b912ad7c1588f2e6823e44da199dbb18303be141e9b9e8a7f5053f9157d2
status: generated
---

# Work with staleness and maintenance

Use the staleness and maintenance system when you need to detect which help templates are out of sync with their source code and regenerate outdated documentation.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/staleness.py` and `src/attune_author/maintenance.py`

## Check template staleness

1. **Import the staleness module:**
   ```python
   from attune_author.staleness import check_staleness
   from attune_author.manifest import FeatureManifest
   ```

2. **Load the feature manifest:**
   ```python
   manifest = FeatureManifest.from_file("manifest.yaml")
   ```

3. **Run the staleness check:**
   ```python
   report = check_staleness(manifest, "help", ".", features=["your-feature"])
   ```

4. **Review the results:**
   Check `report.stale_count()` and `report.stale_features()` to see which templates need regeneration.

## Run maintenance to update stale templates

1. **Import the maintenance module:**
   ```python
   from attune_author.maintenance import run_maintenance
   ```

2. **Run maintenance with dry-run first:**
   ```python
   result = run_maintenance("help", ".", dry_run=True)
   print(f"Would regenerate {result.stale_count()} templates")
   ```

3. **Execute the actual maintenance:**
   ```python
   result = run_maintenance("help", ".", dry_run=False)
   print(f"Regenerated {result.regenerated_count()} templates")
   ```

## Set up automatic maintenance with git hooks

1. **Configure the post-commit hook:**
   ```python
   from attune_author.maintenance import run_hook
   result = run_hook("help", ".")
   ```

2. **Add to your `.git/hooks/post-commit` file:**
   ```bash
   #!/bin/bash
   python -c "from attune_author.maintenance import run_hook; run_hook('help', '.')"
   ```

3. **Make the hook executable:**
   ```bash
   chmod +x .git/hooks/post-commit
   ```

## Verify success

Your maintenance is working correctly when:
- `check_staleness()` returns a report with `stale_count() == 0`
- `run_maintenance()` returns a result showing the expected number of regenerated templates
- Git hooks automatically update templates after commits that modify source files

## Key files

- `src/attune_author/staleness.py` — Core staleness detection logic
- `src/attune_author/maintenance.py` — Template regeneration and git hook integration
