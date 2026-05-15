# Spec: Polish Fact-Check

> Reduce attune-author polish-pass hallucinations through automated
> verification. Umbrella spec; ships as four sequential PRs (Phases 1–4).

---

## Phase 1: Requirements

**Status**: draft

### Problem statement

The attune-author polish pass routinely invents plausible-sounding surface
details that don't exist in the source files it was given. Concrete evidence
from a single feature regen (attune-ai's `ops-dashboard`, 2026-05-14, see
[attune-ai PR #351](https://github.com/Smart-AI-Memory/attune-ai/pull/351)):

| Failure class | Count | Example |
|---|---|---|
| Hallucinated CLI flag | 1 | `--allow-run` (real: `--read-only`, inverted semantics) |
| Hallucinated private module path | 2 | `from attune.ops._readers import …` (`ModuleNotFoundError`) |
| Hallucinated cross-references | 4 | `Concept: Template design patterns` (no such doc) |
| Hallucinated count | 1 | `498 templates` (real: 259) |
| Wrong route path | 2 | `POST /run` (real: `POST /workflows/{name}/run`) |
| Insecure example | 1 | `host="0.0.0.0"` with no auth callout |

Six distinct factual errors in a single feature's docs. Of these, three
(the CLI flag, the private import, and the wrong route) actively break
readers who follow the documentation literally. The current mitigation is
a manual editorial pass per feature — expensive, doesn't scale to the
remaining 9 stale features, and worse: it doesn't scale to a
weekly-or-faster regen cadence which is the whole premise of the living
help system.

All six failure modes share a pattern: the LLM is filling in surrounding
scaffolding from priors rather than being constrained to the source
files it was given. The fix is to **shift verification work from human
review to automated checks**, while keeping the polish pass's freedom to
phrase, organize, and elaborate.

### Scope

**In scope:**

- A four-phase intervention ladder, each phase shipping as its own PR:
  1. **AST-based post-generation fact-check** — Python-AST + CLI-help +
     Markdown-link verification of polished output. Soft-fail (emit an
     `## Unresolved references` block) initially; configurable to
     strict-fail later.
  2. **Inject ground-truth context into the polish prompt** — for any
     feature with a CLI surface, render `--help` output and inject it
     under a `<cli_help>` sentinel tag in the prompt. Same for module
     `__all__` and dataclass field lists.
  3. **Adapt the attune-rag faithfulness judge to polish output** — run
     each polished file through `attune_rag.eval.faithfulness.FaithfulnessJudge`
     against the source files; flag for review when score is below a
     configurable threshold (default `0.95`).
  4. **Static analysis of tutorial code samples** — for `docs/tutorials/*.md`
     specifically, extract Python code fences and run `mypy --strict` +
     `ast.parse` against each. Catches the entire `_readers`/`_models`
     hallucination class without executing untrusted code.
- A regression fixture: the ops-dashboard editorial pass diffs from
  attune-ai PR #351 form a ground-truth set. Every check must catch the
  errors that pass actually fixed.

**Out of scope:**

- Phase 4.2: actual execution of tutorial samples (Tier 1–3 sandboxing).
  Discussed in the design doc as a future follow-up; gated on Phase 4.1
  data showing static analysis isn't sufficient.
- Polish prompt-engineering changes unrelated to ground-truth injection
  (Phase 2 is narrowly scoped to context-injection, not prompt rewriting).
- Changes to the attune-rag faithfulness judge itself; Phase 3 only
  *uses* the existing judge.
- Cost-side changes to the polish pass — none of the four phases changes
  per-feature LLM cost beyond Phase 3's additional Haiku call (~$0.01-0.05
  per file).

### Acceptance criteria

**Per-phase exit criteria** are documented in `design.md` and `tasks.md`.
For the umbrella spec to be considered complete:

1. **Phase 1 ships and the ops-dashboard regression fixture is reduced
   from 6 errors → ≤1 error**. The remaining error is the
   missing-security-callout for the `0.0.0.0` example — a genuinely
   different failure shape (missing content, not wrong content) that
   Phase 3 (faithfulness judge) is better suited to catch. Phase 1
   covers 5 of 6: Python refs, CLI refs, Markdown links, and **numeric
   claims** (promoted from stretch to required per the decision matrix).
2. **Phases 2–4 ship in order**, each with its own PR and its own
   regression delta against the same fixture.
3. **No regression in polish output quality** — measured by spot-checking
   3 features post-Phase-4 against pre-Phase-1 versions. The polish pass
   should write *less* invented scaffolding, not less useful content.
4. **All four checks are configurable** — thresholds, severities, and
   opt-out per-feature via `pyproject.toml` `[tool.attune-author.fact-check]`.

### Non-goals / explicitly deferred

- **Strict-fail by default in Phase 1**. The soft-fail default lets us
  measure noise vs signal before tightening the gate. Pattern matches
  the test-quality-program rubric's "measure first, gate later"
  approach.
- **CI integration**. All four checks run during `attune-author generate`
  / `attune-author regenerate`. CI integration (failing builds when
  docs/ has unresolved references) is a follow-up after Phase 4 lands.
- **Generalizing beyond attune-ai's docs**. The fact-check operates on
  any feature's generated templates; it doesn't assume the consumer is
  attune-ai. But the regression fixture comes from attune-ai's
  ops-dashboard, and we won't try to validate against arbitrary
  third-party usage in this spec.

### Decisions

Pre-committed decisions live in [`decisions.md`](./decisions.md) and are
the source of truth. Calibration records and decision-change history
also live there.

### Risks

| Risk | Severity | Mitigation |
|---|---|---|
| AST checks produce too many false positives (soft-fail noise drowns signal) | Med | Soft-fail blocks at file bottom are scannable; track soft-fail rate per regen and tune resolvers |
| Phase 2 context injection blows polish prompt budget | Low | Measure context size before/after on the ops-dashboard fixture; cap injection at 5KB |
| Phase 3 faithfulness judge disagrees with our regression fixture | Med | Calibrate threshold against the ops-dashboard fixture before defaulting; document calibration |
| Phase 4 mypy false positives on legitimate `# type: ignore` patterns | Low | Allow `# attune-author: skip-mypy` frontmatter on individual samples |
| Bundled umbrella spec gates Phase 1 on broader approval than it needs | Low | Phase 1 framed as the "buy your way to value first" entry; explicitly approvable without committing to Phases 2–4 |
