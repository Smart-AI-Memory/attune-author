# Design — doc-automation-consolidation

**Status:** Draft (2026-06-14)
**Owner:** Patrick

Embodies recommendations 1–5 from the 2026-06-14 discussion.

---

## 1. Ownership boundaries (recommendation 1 + 3)

| Repo | Owns | Does NOT |
|---|---|---|
| **attune-author** | The automation **engine**: generate, polish, staleness (content-hash), regen-on-drift, faithfulness, **and honoring the maintenance contract**. The single LLM auth path (`auth.py`). | Reading/serving docs; workflow orchestration. |
| **attune-help** | Reading / serving the corpus to humans + AI over MCP. | Generation/polish. |
| **attune-ai** | **Orchestration only** — invoking attune-author and surfacing results inside workflows (dashboards, MCP tools). | Reimplementing polish/regen. Delete the `help/polish.py` fork (F1). Fix/remove the broken in-process call (F2). |

Net effect: one engine, one auth path. attune-ai's keyless-vs-key
confusion dissolves because it no longer has its own key-only polish.

## 2. The maintenance contract (recommendations 2 + 4)

A per-page, three-state contract — not a boolean:

- `auto` — fully generated; regen may overwrite freely.
- `manual` — human-owned; regen never writes. Drift is reported, not
  corrected.
- `hybrid` — generated skeleton with hand-written regions; regen
  rewrites only the auto regions, preserving marked manual regions.

**Source of truth = the page's own frontmatter** (e.g.
`maintenance: manual`). Rationale:

- Travels with the content (survives moves/renames).
- Visible to whoever edits the page.
- Cannot silently drift from reality the way a separate central
  registry does.

**The "registry" is a derived view, not the truth.** A generated
report enumerates every page and its mode for auditing. For `hybrid`,
manual regions are delimited by explicit markers (exact marker syntax
is an open decision — see decisions.md).

### Why this is load-bearing, not a footnote

Staleness is detected by content hash. A human-edited page always
hashes as "drifted," so without the contract the engine regenerates
over it — automation fights the editor. The contract is the safety
net that makes broadened automation safe (constraint C1).

## 3. The integration boundary (recommendation 3 — OPEN DECISION)

attune-ai consumes attune-author two ways today (F5): subprocess CLI
(regen/status) and a lazy in-process import (the broken polish). The
spec must pick the target boundary explicitly. Trade-offs:

| | Subprocess (CLI) | In-process (import) |
|---|---|---|
| Coupling | Loose; clean process boundary | Tight; shared objects/auth |
| Dep tier | Stays optional `[author]` extra | Becomes a closer runtime dep |
| Data | Text across boundary (must parse, C2) | Structured returns, streaming |
| Auth | Subprocess inherits `CLAUDECODE` → keyless works | Shares author's `auth.py` directly |
| Cost | Process startup per call | None |
| Versioning | Looser; CLI contract | Lockstep PyPI releases |

**Recommendation:** keep **regen/status on the subprocess boundary**
(it already works keyless and is loosely coupled) and **fix the
memory-polish path by switching it to the same subprocess/CLI call or
removing it** — rather than deepening the in-process import. This
avoids turning attune-author into a heavier runtime dep and avoids
PyPI lockstep. Final call recorded in decisions.md.

## 4. Auth, restated

One path lives in attune-author's `auth.py` (subscription-first under
Claude Code, API-key fallback, Batches always key-required). Once
attune-ai routes its doc work through attune-author (subprocess
inherits `CLAUDECODE`), the doc-polish path is keyless for free. No
`attune_ai.auth` helper is introduced (consistent with the
sibling-subscription-auth decision to accept per-package adapters).

## 5. Sequencing (recommendation 5)

Contract first (safety net), then consolidation, so automation is
never broadened over curated pages while the net is missing:

1. Maintenance contract in attune-author (parse + honor + report).
2. Consolidation in attune-ai (delete fork, fix/remove broken call,
   route through the one engine).
3. Boundary + dep/version policy made explicit and the cap bumped
   only after the status-format contract (C2) is confirmed stable.

Each step keeps every repo independently releasable (C4).
