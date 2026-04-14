---
type: quickstart
feature: staleness-and-maintenance
depth: quickstart
generated_at: 2026-04-14T14:06:47.087055+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Quickstart: staleness and maintenance

Check which help templates are stale and automatically regenerate them.

```python
from attune_author.staleness import run_maintenance

# Check for stale templates and regenerate them
result = run_maintenance("docs/help", ".")
print(f"Found {result.stale_count} stale features")
print(f"Regenerated {result.regenerated_count} templates")
```

## Check staleness without regenerating

To see which templates are out of date without changing anything:

```python
from attune_author.staleness import check_staleness
from attune_author.core import load_manifest

manifest = load_manifest("docs/help")
report = check_staleness(manifest, "docs/help", ".")
print(f"Stale features: {report.stale_features}")
```

## Set up automatic maintenance

Add a post-commit hook to regenerate templates when source files change:

```python
from attune_author.staleness import run_hook

# Returns None if no files changed, otherwise MaintenanceResult
result = run_hook("docs/help", ".")
if result:
    print(f"Updated {result.regenerated_count} templates")
```

Expected output when templates are regenerated:
```
Found 2 stale features
Regenerated 2 templates
```

## Next steps

Read the [maintenance concept guide](../concepts/maintenance.md) to understand how staleness detection works and when templates are considered out of date.
