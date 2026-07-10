---
type: concept
name: staleness-and-maintenance-concept
feature: staleness-and-maintenance
depth: concept
generated_at: 2026-07-10T13:08:07.296131+00:00
source_hash: f70ee7dc8566b26c31c6469a302951de9b7e530870798083457598b8f84d96d6
status: generated
scaffold_hash: 987852496b6fe69ac7a1a507a34fbced646796239d8ab2abd62e795c53829149
---

# Staleness and maintenance

Staleness detection tells you when generated help templates and project docs have drifted from the source code they describe, and maintenance regenerates the stale ones.

## How it works

Generated documentation rots when source code changes underneath it. This feature closes that gap with a hash-compare-regenerate loop across two modules: `attune_author.staleness` (detection) and `attune_author.maintenance` (repair).

The cycle works like this:

1. **Record.** When a doc is generated, `build_doc_footer` writes an HTML comment footer into the file that records the source hash, feature name, doc kind, and generation timestamp.
2. **Hash.** Later, `compute_source_hash` computes a SHA-256 hash of a feature's current source files. `compute_semantic_hash` does the same but hashes the semantic content of the Python source, so cosmetic edits don't trigger false staleness. Cache and tooling directories such as `__pycache__` and `node_modules` are excluded from hashing.
3. **Compare.** `check_staleness` reads each doc's stored hash (via `parse_doc_footer`) and compares it against the current hash. `check_workspace_staleness` does the same for a workspace that uses the conventional `.help/` layout. Both return a `StalenessReport`.
4. **Regenerate.** `run_maintenance` acts on the report: it regenerates stale docs and returns a `MaintenanceResult` describing what happened. Pass `dry_run=True` to see what would be regenerated without touching any files.

Two entry points feed this cycle automatically:

- `run_hook` is the post-commit hook entry point. It uses `get_changed_files` to look at the most recent commit, so routine commits keep help content fresh without manual effort.
- `format_status_report` turns a `StalenessReport` into human-readable output when you want to inspect drift yourself.

### The report structures

A `StalenessReport` aggregates two kinds of entries plus an exclusion list:

- **`FeatureStaleness`** — status for one feature's `.help/` templates. Its `is_stale` flag is derived by comparing `current_hash` against `stored_hash`; `matched_files` lists the source files that contributed to the hash.
- **`DocStaleness`** — status for one project doc file in `docs/`. In addition to the hash pair, its `missing` flag distinguishes a doc that has drifted from one that was never generated or has been deleted.
- **`manual_features`** — features whose docs are hand-maintained and should never be regenerated.

Convenience properties on the report (`stale_count`, `current_count`, `stale_features`, `stale_docs`) let callers summarize or filter without walking the entry lists themselves.

A `MaintenanceResult` mirrors this shape for the repair side: it carries the triggering `staleness` report, the list of `regenerated` docs, features `skipped_manual` because they're hand-maintained, and any that `failed`. Its `stale_count` and `regenerated_count` properties give you the before-and-after numbers at a glance.

## What connects to it

Staleness and maintenance sits between doc generation and version control: generation stamps the footer, commits trigger the check, and regeneration feeds back into generation.

Other parts of the codebase interact with this feature through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `MaintenanceResult` | Result of a help maintenance run | `src/attune_author/maintenance.py` |
| `FeatureStaleness` | Staleness status for one feature's `.help/` templates | `src/attune_author/staleness.py` |
| `DocStaleness` | Staleness status for one project doc file in `docs/` | `src/attune_author/staleness.py` |
| `StalenessReport` | Combined staleness report across help templates and project docs | `src/attune_author/staleness.py` |

If you only need to answer "is anything stale?", call `check_workspace_staleness` and read `stale_count`. If you need to fix drift, call `run_maintenance` — or install the post-commit hook so `run_hook` does it for you.
