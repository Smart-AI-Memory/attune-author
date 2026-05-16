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
- 2026-05-16 — Phase 2 shipped. New decisions captured during
  implementation:
  - **Composition with RAG context**: ground-truth context is
    prepended to the RAG hook's existing `augmented_context` rather
    than replacing it. Rationale: the two carry orthogonal information
    (RAG retrieves similar templates; ground-truth pins names) so
    keeping both maximizes prompt utility within the budget.
  - **Anchor clause as system-prompt suffix**: the
    `ANCHORING_CLAUSE` appends to the existing per-template-type
    system prompt rather than replacing or wrapping it. Rationale:
    minimises drift from the existing polish system prompts, which are
    already large (~6KB) and cache-friendly; the suffix is short and
    behaviorally additive.
  - **Cache-key participation**: when the anchor clause is added,
    the system prompt changes — and the polish-cache key already
    includes the system prompt, so existing cached entries are
    invalidated cleanly without bespoke cache-key plumbing.
  - **CLI flags deferred (task 2.8)**: env-driven defaults via
    `[tool.attune-author.context-injection]` in `pyproject.toml`
    were sufficient for the first iteration. CLI flags can be added
    in a follow-up alongside Phase 3's `--faithfulness-threshold`
    flag.
  - **Live-LLM acceptance gate deferred**: task 2.10 splits into
    a unit-level part (assert sentinel blocks reach the user
    message + anchor clause reaches the system prompt — done) and
    a live-LLM part (actually polish ops-dashboard with Phase 2 on
    + Phase 1 off and observe 0/3 high-severity errors). The
    live-LLM part stays gated behind real-API-key availability.
  - **Cost-delta measurement deferred to Phase 3**: when the
    faithfulness judge ships, it will require its own real-LLM
    calibration run. Folding the cost-delta measurement into that
    run avoids two separate real-LLM cycles.
- 2026-05-16 — Phase 3 shipped. New decisions captured during
  implementation:
  - **Opt-in default**: `enabled=False` ships in
    `FaithfulnessConfig` and the pyproject loader, because the
    judge makes real Anthropic API calls and we shouldn't bill
    users for it silently on the first run after install. The
    Phase 1 fact-check is enabled by default (no API calls); the
    Phase 3 judge is not.
  - **Synchronous wrapper via `asyncio.run`**: the existing
    polish pipeline is synchronous, so the async
    `FaithfulnessJudge.score` coroutine is bridged with
    `asyncio.run`. This precludes calling the judge from inside
    a running event loop (we don't, today), but keeps the
    surface aligned with the rest of attune-author.
  - **Best-effort vs strict**: missing extras / missing API key
    / transient failures all default to `JudgeOutcome(score=None,
    skipped_reason=…)` rather than raising. CI lanes that need
    loud failures opt in via `block_polish_on_unavailable = true`.
  - **Budget gate uses character-count heuristic, not tokenizer**:
    `estimate_cost_usd(chars, model)` divides chars by 4 to get
    a rough token count and multiplies by a per-model price
    lookup. Accurate to ~20% — well inside what a $0.10 budget
    cap cares about. A real tokenizer is a future change if
    drift surfaces.
  - **Cost telemetry as function attribute, not module global**:
    `_faithfulness_telemetry()` stores the counter dict on its
    own `_state` attribute so it's resettable, mockable, and
    doesn't leak module-level state. Mirrors how the polish
    cache exposes its store.
  - **Calibration deferred**: tasks 3.3 and 3.4 require a real
    LLM run against the ops-dashboard pre-fix and post-fix
    fixtures. The placeholder threshold of `0.95` ships as the
    default and the calibration is scheduled to land alongside
    the live-LLM Phase 2 acceptance run so a single real-API
    cycle covers both phases' open work.
