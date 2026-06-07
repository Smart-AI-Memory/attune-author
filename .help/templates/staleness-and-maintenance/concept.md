---
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-06-06T23:19:48.572962+00:00
source_hash: a32e9d9904602f0f282f0bf02f119e350efd6c8b4ecb73c04564917b6ae65f69
status: generated
---

# Staleness And Maintenance

## How it works

Detect when generated templates are out of date with their source files and regenerate stale ones
.

The main building blocks are:

- **`FeatureStaleness`** — Staleness status for one feature's ``.help/`` templates.
- **`DocStaleness`** — Staleness status for one project doc file in ``docs/``.
- **`StalenessReport`** — Combined staleness report across help templates and project docs.
- **`MaintenanceResult`** — Result of a help maintenance run.

Under the hood, this feature spans 2 source
files covering:

- Help maintenance logic for commit hooks and manual refresh.

## What connects to it

This feature relates to: freshness, hashing, regeneration.

Other parts of the codebase interact with
staleness and maintenance through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `FeatureStaleness` | Staleness status for one feature's ``.help/`` templates. | `src/attune_author/staleness.py` |
| `DocStaleness` | Staleness status for one project doc file in ``docs/``. | `src/attune_author/staleness.py` |
| `StalenessReport` | Combined staleness report across help templates and project docs. | `src/attune_author/staleness.py` |
| `MaintenanceResult` | Result of a help maintenance run. | `src/attune_author/maintenance.py` |
