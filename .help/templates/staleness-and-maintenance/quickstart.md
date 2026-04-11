---
type: quickstart
feature: staleness-and-maintenance
depth: quickstart
generated_at: 2026-04-11T04:54:40.306769+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Quickstart: staleness and maintenance

Check which help templates are outdated and regenerate them automatically:

```python
from attune_author.staleness import check_staleness
from attune_author.manifest import load_manifest

manifest = load_manifest("help/manifest.yaml")
report = check_staleness(manifest, "help", ".")
print(f"Found {report.stale_count()} stale templates")
```

## Check template staleness

Run a staleness check to see which templates need updating:

```python
from attune_author.staleness import check_staleness, format_status_report
from attune_author.manifest import load_manifest

manifest = load_manifest("help/manifest.yaml")
report = check_staleness(manifest, "help", ".")
print(format_status_report(report, "help"))
```

Expected output:
```
Staleness Report for help/
3 features current, 1 stale
Stale features: api-client
```

## Regenerate stale templates

Update outdated templates with a single command:

```python
from attune_author.maintenance import run_maintenance

result = run_maintenance("help", ".", dry_run=False)
print(f"Regenerated {result.regenerated_count()} templates")
```

Expected output:
```
Regenerated 1 templates
```

## Set up automated maintenance

Add the post-commit hook to regenerate templates after code changes:

```python
from attune_author.maintenance import run_hook

# Call this from your git post-commit hook
result = run_hook("help", ".")
if result:
    print(f"Auto-regenerated {result.regenerated_count()} templates")
```

**Next:** Set up the [git post-commit hook](../how-to/setup-git-hooks.md) to automate template maintenance.
