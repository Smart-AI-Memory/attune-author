---
type: tip
feature: staleness-and-maintenance
depth: tip
generated_at: 2026-04-11T04:54:49.846933+00:00
source_hash: ef4c74abf7547edaa6f0d693a7097d1cff76652402f49144080c3f03136dfb6e
status: generated
---

# Tip: working effectively with staleness and maintenance

Use `check_staleness()` before `run_maintenance()` when you need visibility into what will change. The maintenance function regenerates stale templates automatically, but checking staleness first lets you see the scope of work and decide whether to proceed.

## Why this matters

Running maintenance blindly can regenerate dozens of templates unexpectedly, making it hard to review what actually changed in your commit.

## Tradeoff

The two-step approach requires an extra function call, but the visibility is worth it for any non-trivial maintenance run where you care about reviewing the output.

## Source files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

**Tags:** `freshness`, `hashing`, `regeneration`
