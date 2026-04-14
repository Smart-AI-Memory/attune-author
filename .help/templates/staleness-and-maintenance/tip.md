---
type: tip
feature: staleness-and-maintenance
depth: tip
generated_at: 2026-04-14T16:11:49.039176+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Run staleness checks before manual template updates

Use `check_staleness()` to identify outdated templates before you start editing them manually. This prevents you from polishing templates that will be overwritten by the next regeneration cycle, saving time and avoiding frustration when your careful edits disappear.

The `StalenessReport` shows exactly which features need attention through its `stale_features` property, and you can scope the check to specific features with the optional `features` parameter.

**Tradeoff:** Running staleness checks adds a few seconds to your workflow, but manual edits to stale templates are always wasted effort.
