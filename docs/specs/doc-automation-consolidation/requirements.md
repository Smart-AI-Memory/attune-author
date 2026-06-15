# Requirements — doc-automation-consolidation

**Status:** approved
(2026-06-14)
**Owner:** Patrick
**Mode:** planning (no code changes in this spec phase)

---

## Problem

Documentation-update automation is forked across the three repos and
the copies have drifted (see [findings.md](findings.md)):

- attune-author polishes keyless under Claude Code; attune-ai's copy
  is key-only (F1).
- attune-ai's in-process polish call has silently never worked (F2).
- Each repo owns overlapping doc surfaces with no single home for the
  automation engine or for *which pages are hand-maintained* (F7).

The result: confusing auth behavior, dead integration code, and risk
that broadened automation will overwrite human-curated pages.

## Outcome (what should be true when done)

1. There is **one** documentation-automation engine, owned by
   attune-author. No second polish/regen implementation elsewhere.
2. Every documentation page declares a **maintenance contract**
   (`auto | manual | hybrid`); the engine honors it and never
   clobbers human-maintained content.
3. attune-ai *invokes* the engine and surfaces results; it does not
   reimplement it. The keyless-vs-key confusion disappears because
   there is one auth path.

## Goals

- **G1** Single home: consolidate doc generate/polish/staleness/regen/
  faithfulness in attune-author.
- **G2** Safety: a maintenance-mode contract that makes manual and
  hybrid pages first-class, so automation augments rather than
  overwrites.
- **G3** Clarity: delete attune-ai's forked `help/polish.py`; fix or
  remove the broken in-process call (F2); one auth path.
- **G4** An explicit, written decision on the integration boundary
  (subprocess vs in-process, dep tier, version policy).

## Non-goals

- The full three-repo MCP namespace consolidation (`help_*` /
  `lookup_*` / `author_*`) — adjacent, tracked separately (F7). Keep
  boundaries compatible but do not fold it in here.
- Subscription auth for the Batches API — no subscription path exists
  (F3); batch stays key-required by design.
- Rewriting attune-help's reader surface.

## Constraints

- **C1** Content-hash drift detection treats human edits as drift;
  the maintenance contract MUST land before/with any broadened
  automation, or curated pages get clobbered (the sequencing rule).
- **C2** attune-ai parses `attune-author status` output as markdown
  (F5); any status-format change must preserve or version that
  contract.
- **C3** attune-help is pinned explicitly in attune-ai since author
  0.15.0 dropped it transitively (F6); dep-tier changes must respect
  this.
- **C4** Cross-repo, cross-PyPI: changes ship as coordinated releases.
  Prefer a sequencing that keeps each repo releasable on its own.

## Acceptance criteria

- [ ] attune-ai has no second polish implementation; `help/polish.py`
      fork removed or reduced to a thin call into attune-author.
- [ ] The broken `polish_template` call (F2) is fixed or removed —
      no silent no-op remains.
- [ ] Pages can be marked `auto | manual | hybrid`; a regen run skips
      `manual`, regenerates only auto regions of `hybrid`, and never
      overwrites manual content (covered by a regression test).
- [ ] A derived report lists each page's maintenance mode (generated,
      not hand-maintained).
- [ ] The integration-boundary decision is recorded in
      [decisions.md](decisions.md) with rationale.
