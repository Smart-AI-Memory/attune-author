---
type: troubleshooting
feature: staleness-and-maintenance
depth: troubleshooting
generated_at: 2026-04-11T04:54:12.489046+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Troubleshoot staleness and maintenance

## Before you start

This feature detects when generated help templates are out of date with their source files and regenerates stale ones. Use this guide when staleness checks fail or maintenance operations don't behave as expected.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `FileNotFoundError` during staleness check | Verify `help_dir` and `project_root` paths exist and are accessible |
| Hash computation fails | Run `compute_source_hash()` directly with the failing feature to see the exact error |
| Wrong staleness results | Compare source file timestamps with generated template timestamps in the help directory |
| Maintenance runs but doesn't regenerate | Check if `dry_run=True` or if the feature list excludes your target features |
| Hook doesn't trigger after commit | Verify `run_hook()` is properly configured in your git post-commit hook |

## Step-by-step diagnosis

1. **Test staleness detection in isolation.**
   Run a minimal staleness check to confirm the basic mechanism works:
   ```python
   from attune_author.staleness import check_staleness
   from attune_author.manifest import load_manifest

   manifest = load_manifest("path/to/manifest.yml")
   report = check_staleness(manifest, "help/", ".", features=["your-feature"])
   print(f"Stale: {report.stale_count()}, Current: {report.current_count()}")
   ```

2. **Check hash computation.**
   If staleness detection seems wrong, verify the source hash calculation:
   ```python
   from attune_author.staleness import compute_source_hash
   from attune_author.manifest import load_manifest

   manifest = load_manifest("path/to/manifest.yml")
   feature = manifest.features["your-feature"]
   hash_val, files = compute_source_hash(feature, ".")
   print(f"Hash: {hash_val}, Files: {files}")
   ```

3. **Enable maintenance dry-run mode.**
   Test what maintenance would do without making changes:
   ```python
   from attune_author.maintenance import run_maintenance

   result = run_maintenance("help/", ".", dry_run=True)
   print(f"Would regenerate {result.regenerated_count()} of {result.stale_count()} stale features")
   ```

4. **Inspect file change detection.**
   If the post-commit hook isn't working, check what files it detects:
   ```python
   from attune_author.maintenance import get_changed_files

   changed = get_changed_files(".")
   print(f"Changed files: {changed}")
   ```

## Common fixes

- **Fix missing directories.** Create the help directory if it doesn't exist:
  ```bash
  mkdir -p help/
  ```

- **Update stale git hooks.** Ensure your post-commit hook calls `run_hook()`:
  ```bash
  # In .git/hooks/post-commit
  #!/bin/bash
  python -c "from attune_author.maintenance import run_hook; run_hook('help/', '.')"
  ```

- **Clear template cache.** Remove generated templates to force regeneration:
  ```bash
  find help/ -name "*.md" -type f -delete
  ```

- **Check file permissions.** Ensure the process can read source files and write to the help directory:
  ```bash
  chmod -R u+rw help/
  chmod -R u+r src/
  ```

- **Verify manifest syntax.** Invalid YAML in the feature manifest can break staleness detection:
  ```bash
  python -c "import yaml; yaml.safe_load(open('manifest.yml'))"
  ```

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
