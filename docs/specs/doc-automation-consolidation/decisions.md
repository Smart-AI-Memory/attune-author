# Decisions — doc-automation-consolidation

**Status:** Draft (2026-06-14) — D1–D4 settled; D5/D6 non-blocking
**Owner:** Patrick

---

## Settled

- **S1 — attune-author is the single home for doc automation.**
  Evidence: forked + diverged polish (F1), broken in-process call
  (F2). Direction confirmed in the 2026-06-14 discussion.
- **S2 — Maintenance contract is a 3-state, frontmatter-sourced
  contract** (`auto | manual | hybrid`), with a *derived* report —
  not a hand-maintained central registry. (design §2)
- **S3 — Contract before consolidation.** Sequencing is fixed by
  constraint C1 (hash drift would clobber manual pages).
- **S4 — No `attune_ai.auth`.** One auth path lives in attune-author;
  attune-ai inherits keyless via the subprocess boundary. Consistent
  with sibling-subscription-auth's accept-duplication decision.
- **S5 — Integration boundary = subprocess CLI** (D1 resolved
  2026-06-14, Patrick). attune-author stays an *optional*,
  loosely-coupled dependency invoked as a child process; it inherits
  `CLAUDECODE=1` so the doc-polish path is keyless. No in-process
  import path, no PyPI version lockstep.
- **S6 — Remove the broken memory-polish call** (D2 resolved
  2026-06-14, Patrick). `personal.py:335` is a *semantic* mismatch,
  not a fixable typo: memory capture has no `feature_name` /
  `source_summary` to pass. Delete the dead path. "Polished memories,"
  if wanted, is a separate feature with a memory-appropriate prompt —
  not a salvage of this call.
- **S7 — `hybrid` regions use HTML comment fences** (D3 resolved
  2026-06-14, Patrick): `<!-- attune:manual:start -->` …
  `<!-- attune:manual:end -->`. Invisible when rendered, robust to
  heading renames, simple merge (rewrite outside fences, preserve
  inside). Parse conservatively (matched start/end only), mirroring
  the 0.16 fence-strip fix.
- **S8 — Unmarked pages default to `auto`** (D4 resolved 2026-06-14,
  Patrick), paired with the one-time maintenance report so curated
  pages get flipped to `manual`/`hybrid` without freezing regen.

## Open — non-blocking (do not gate Phase 1)

- **D5 — Cap bump timing.** Bump attune-ai's `attune-author<0.16` to
  `>=0.17` now (low risk for the CLI path, F4/F5) or fold it into the
  consolidation PR? Gated on confirming `status` output format is
  unchanged (C2).
  - *Recommendation:* fold into consolidation; the bump alone fixes
    nothing user-visible (F2) and the CLI path already works keyless.

- **D6 — Spec home / ownership across repos.** This spec lives in
  attune-author (the engine owner), but execution touches attune-ai.
  Mirror a pointer into attune-ai's specs, or drive cross-repo from
  here? (sibling-subscription-auth was driven from attune-ai.)
