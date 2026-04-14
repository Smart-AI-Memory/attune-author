---
type: tip
feature: staleness-and-maintenance
depth: tip
generated_at: 2026-04-14T14:06:54.508816+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Check staleness before regenerating help templates

Start with `check_staleness()` to see what's out of date, then decide whether to regenerate automatically or manually review each stale template.

This prevents you from regenerating templates unnecessarily and gives you control over which features to update. The `StalenessReport` shows exactly which source files changed for each stale feature, so you can assess whether the changes warrant template updates.

**Tradeoff:** Takes an extra step compared to running `run_maintenance()` directly, but saves time when only a few features need updates or when you want to review changes before regenerating.
