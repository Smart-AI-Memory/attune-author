---
type: comparison
feature: staleness-and-maintenance
depth: comparison
generated_at: 2026-04-14T16:12:05.139161+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness detection vs manual help template management

## What each approach offers

| Feature | Staleness detection | Manual management |
|---------|-------------------|-------------------|
| **Accuracy** | SHA-256 hash tracking ensures templates match source | Relies on developer memory and discipline |
| **Speed** | Batch operations check all features in ~100ms | Manual checks scale linearly with feature count |
| **Integration** | Post-commit hooks catch changes automatically | Requires remembering to run updates |
| **Selective updates** | Can target specific features or process all stale ones | Full control over what gets regenerated |
| **Error handling** | Tracks failed regenerations and skipped manual features | No systematic error reporting |
| **Overhead** | Requires `.help/hashes.yaml` storage file | No additional files |

## Key capabilities comparison

**Staleness detection provides:**
- `check_staleness()` — Compare stored hashes against current source state
- `run_maintenance()` — Detect and regenerate stale templates in one operation
- `run_hook()` — Automatic updates on git commits
- Detailed reporting through `StalenessReport` and `MaintenanceResult`

**Manual management gives you:**
- Direct control over regeneration timing
- No dependency on hash storage
- Simpler workflow for one-off updates
- No risk of automatic overwrites

## Use staleness detection when

- You work on a team where multiple people modify source files
- Your project has more than 5-10 features (manual tracking becomes error-prone)
- You want automatic updates triggered by git commits
- You need to verify which templates are current without regenerating them
- You're building CI pipelines that need to catch stale documentation

## Use manual management when

- You're prototyping features and templates change frequently
- Your project has fewer than 5 features
- You prefer explicit control over when templates regenerate
- You're working solo and can reliably remember to update templates
- Storage overhead from hash tracking matters for your use case

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
