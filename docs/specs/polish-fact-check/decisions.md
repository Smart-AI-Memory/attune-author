# Spec: Polish Fact-Check — Decisions

> Pre-committed decisions per the existing lesson "Pre-committed
> decision matrices survive contact with data." Edits to this file
> after Phase 1 ships require a follow-up PR with rationale.

---

## Decision matrix

| Decision | Choice | Rationale |
|---|---|---|
| Phase 1 default failure mode | Soft-fail (`## Unresolved references` block at bottom of file) | Lets us measure noise vs signal before tightening the gate. Mirrors test-quality-program's "measure first, gate later" rubric pattern. |
| Phase 1 strict-fail escalation criterion | Move to strict-fail if soft-fail rate drops below 5% across two consecutive **weekly** regens | Weekly cadence matches the help-system's intended regen rhythm; monthly would delay the escalation decision unnecessarily. |
| Phase 1 numeric-claim check | Required (not stretch) | Patrick tightened the acceptance gate from 4/6 to 5/6 errors caught at Phase 1 ship. Numeric claims are AST-pattern-detectable; only the "missing security callout" failure mode stays for Phase 3. |
| Phase 1 CLI-ref version coupling | Acceptable, with proactive user messaging | When a flag isn't found in `attune <cmd> --help`, the finding message includes (a) the installed attune-ai version, (b) instructions to verify against the target version, (c) override snippet. See `design.md` § Check 2. |
| Phase 3 default faithfulness threshold | `0.95` (mean across paragraphs in a single file) | Untested at spec-draft time. Will be **calibrated** against the ops-dashboard regression fixture in Phase 3 task #3.3 before defaulting. If calibration shows pre-fix mean ≥ 0.9 or post-fix mean < 0.95, the threshold gets re-decided. |
| Phase 3 threshold override mechanism | `pyproject.toml` `[tool.attune-author.fact-check]` + per-invocation CLI flag | Two-level override: project-wide config for sustained policy, CLI flag for one-off runs. |
| Phase 3 budget cap | Skip judge call if estimated cost > `$0.10` for a single feature regen | Hard cap protects against unexpected cost when regenerating a feature with many kinds. Configurable. |
| Phase 4 default | Tier 0 (static analysis only); execution requires explicit opt-in | Static analysis catches the documented failure modes (e.g. `_readers` private-module hallucinations) without executing untrusted LLM-generated code. Execution tiers documented in design.md for Phase 4.2 follow-up. |
| Phase 4 execution opt-in mechanism | `# attune-author: exec` frontmatter on individual code samples | Sample-level granularity, not file-level — keeps the human reviewer responsible for confirming each blessed sample has no side effects. |
| Spec-file convention going forward | Include `decisions.md` alongside `requirements.md` / `design.md` / `tasks.md` | Patrick's call (2026-05-14). Extracts pre-committed decisions from the spec body so they're easy to audit and update independently. |

---

## Calibration record

To be filled in during Phase 3 implementation:

- [ ] **Phase 3 threshold calibration** — Phase 3 task #3.3 / #3.4
  - Pre-fix ops-dashboard mean faithfulness score: _TBD_
  - Post-fix ops-dashboard mean faithfulness score: _TBD_
  - Default threshold after calibration: _TBD_

---

## Decision-change log

> Append entries here when a decision above is revised. Reference the PR
> that revised it.

- 2026-05-14 — Initial decisions captured during spec draft. Patrick
  approved.
