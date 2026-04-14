---
type: comparison
feature: staleness-and-maintenance
depth: comparison
generated_at: 2026-04-14T14:07:09.549916+00:00
source_hash: c10710575b8cb6254ba10924c1586487b414a6595a4130159511d0fd6754ca50
status: generated
---

# Staleness detection vs manual help maintenance

## Context

When source code changes, generated help templates become outdated. You can either check for staleness and regenerate automatically, or manually update templates as needed.

## Feature comparison

| Aspect | Staleness detection | Manual maintenance |
|--------|-------------------|-------------------|
| **Accuracy** | SHA-256 hash ensures exact source-template sync | Relies on developer memory and discipline |
| **Speed** | Instant detection across all features | Requires scanning each template individually |
| **Automation** | Integrates with commit hooks for hands-off updates | Every update is a manual decision |
| **Selective updates** | Can target specific features or run across all | Natural granular control |
| **Error prevention** | Catches stale content before it misleads users | Stale templates can persist unnoticed |
| **Setup cost** | Requires initial hook configuration | Works immediately |

## Use staleness detection when...

- You have multiple features that change frequently
- You want to catch outdated help content in CI/CD
- Your team tends to forget manual documentation updates
- You need confidence that help templates match current source code

The automated approach scales better than manual tracking. A single `run_maintenance()` call can check dozens of features in seconds and regenerate only what's actually stale.

## Use manual maintenance when...

- You have a small, stable codebase with infrequent changes
- You want full editorial control over when templates update
- You're working on experimental features that aren't ready for automatic documentation
- You need to coordinate help updates with broader documentation releases

Manual control works well for mature projects where help content changes deliberately rather than reactively.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
