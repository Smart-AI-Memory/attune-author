---
type: quickstart
feature: staleness-and-maintenance
depth: quickstart
generated_at: 2026-04-14T16:11:40.988229+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Quickstart: staleness and maintenance

```python
from attune_author.maintenance import check_staleness
from attune_author.manifest import FeatureManifest

# Check which help templates are out of date
manifest = FeatureManifest.load("help_manifest.toml")
report = check_staleness(manifest, "help/", ".")
print(f"Found {report.stale_count} stale features: {report.stale_features}")
```

## Check template staleness

1. **Load your feature manifest** to get the list of features to check:
   ```python
   from attune_author.manifest import FeatureManifest
   manifest = FeatureManifest.load("help_manifest.toml")
   ```

2. **Run staleness detection** against your help directory:
   ```python
   from attune_author.maintenance import check_staleness
   report = check_staleness(manifest, "help/", ".")
   ```

3. **View the results** to see which templates need updates:
   ```python
   if report.stale_count > 0:
       print(f"Stale templates: {', '.join(report.stale_features)}")
   else:
       print("All templates are up to date")
   ```

Expected output when templates are stale:
```
Stale templates: feature-one, feature-two
```

## Regenerate stale templates

Run maintenance to automatically update outdated templates:

```python
from attune_author.maintenance import run_maintenance
result = run_maintenance("help/", ".")
print(f"Regenerated {result.regenerated_count} templates")
```

**Next:** Set up the [post-commit hook](../reference/staleness-and-maintenance.md#post-commit-hook) to automate staleness detection.
