# Tasks — doc-automation-consolidation

**Status:** Draft (2026-06-14) — Phase 0 settled (D1–D4); Phase 1 ready
**Owner:** Patrick

Sequencing is load-bearing: contract (safety net) before consolidation
(design §5, constraint C1).

---

## Phase 0 — Decisions ✅ settled 2026-06-14

- [x] **0.1** D1 → **subprocess CLI** (S5).
- [x] **0.2** D2 → **remove the broken memory-polish call** (S6).
- [x] **0.3** D3 → **HTML comment fences** (S7).
- [x] **0.4** D4 → **default `auto`** + triage report (S8).
- [ ] **0.5** D6 (spec home / cross-repo ownership) — non-blocking.

## Phase 1 — Maintenance contract in attune-author (the safety net)

- [ ] **1.1** Add frontmatter field `maintenance: auto|manual|hybrid`
      (unmarked ⇒ `auto`, per S8). Define `hybrid` regions as HTML
      comment fences `<!-- attune:manual:start/end -->` (S7).
- [ ] **1.2** Parse the contract in the staleness/regen path.
- [ ] **1.3** Honor it: `manual` → never write (report drift only);
      `hybrid` → rewrite content outside fences, preserve everything
      inside (conservative matched-fence parse, mirroring the 0.16
      fence-strip fix); `auto` → unchanged behavior.
- [ ] **1.4** Regression test: a `manual` page with drift is reported
      but NOT overwritten; a `hybrid` page keeps its fenced regions
      across a regen; unmatched/nested fences fail safe (no clobber).
      (This is the core safety guarantee.)
- [ ] **1.5** Generate the derived maintenance report (page → mode).
- [ ] **1.6** Confirm `attune-author status` output format is
      unchanged for attune-ai's parser, or version it (constraint C2).
- [ ] **1.7** Release attune-author (it stays independently shippable).

## Phase 2 — Consolidate in attune-ai

- [ ] **2.1** Delete / thin `attune-ai/src/attune/help/polish.py` (the
      key-only fork, F1) so there is one polish path.
- [ ] **2.2** Remove the dead memory-polish call (`personal.py:335`
      + the `_load_author`/`_polish` plumbing, F2) per S6. No
      silent-degrade no-op remains.
- [ ] **2.3** Route attune-ai's doc work through the single engine via
      the chosen boundary (D1); confirm keyless under Claude Code.
- [ ] **2.4** Update/extend the integration tests
      (`test_help_data.py`, `test_personal_memory.py`,
      `test_help_regen.py`) — no silent-degrade no-ops remain.

## Phase 3 — Dependency + version policy

- [ ] **3.1** Bump attune-ai's `attune-author<0.16` cap to `>=0.17`
      (per D5), after 1.6 confirms the status-format contract.
- [ ] **3.2** Record the boundary + version policy (lockstep or not)
      in decisions.md as settled.
- [ ] **3.3** Re-validate the attune-help transitive pin (F6) still
      holds under the new arrangement.

## Phase 4 — Close out

- [ ] **4.1** One-time pass: triage existing pages, flip genuinely
      curated ones to `manual`/`hybrid` (uses the 1.5 report + D4).
- [ ] **4.2** Update project memory (engine home, contract, the F2
      bug's resolution). Cross-link the MCP-consolidation backlog (F7)
      so boundaries stay aligned.
