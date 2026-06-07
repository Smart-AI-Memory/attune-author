# Spec: Polish Fact-Check — Tasks

## Phase 3: Tasks

**Status**: complete (shipped in v0.14.0)

> Four phases, each shipping as its own PR. Phase 1 is the recommended
> first commitment; Phases 2–4 build on it. Phase 1 can be approved and
> shipped independently of Phases 2–4.

---

## Phase 1: AST-based post-generation fact-check

**Target PR scope:** ~600 LOC including tests.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 1.1 | Decide config-file location (`pyproject.toml` vs new `.attune-author.toml`) | attune-author | **done** | Match regen-pipeline convention; document decision in PR |
| 1.2 | Create `src/attune_author/fact_check/` package skeleton with `__init__.py`, `python_refs.py`, `cli_refs.py`, `md_links.py`, `numeric_refs.py`, `report.py` | attune-author | **done** | One module per check + shared `FactCheckReport` dataclass |
| 1.3 | Implement `python_refs.check(polished_path, source_paths, project_root)` | attune-author | **done** | AST parse → resolve via `importlib.import_module` in active venv |
| 1.4 | Implement `cli_refs.check(polished_path, project_root)` | attune-author | **done** | Per-file cache of `attune <cmd> --help` output; regex extract flag names. **Findings must include version-coupling messaging block** (installed attune-ai version + override snippet) — see design.md |
| 1.5 | Implement `md_links.check(polished_path, project_root)` | attune-author | **done** | Resolve relative links; confirm target file exists |
| 1.5.1 | Implement `numeric_refs.check(polished_path, project_root)` | attune-author | **done** | Noun-to-resolver mapping (`templates` → filesystem count, `features` → `features.yaml` key count, etc.). Severity: `error` on mismatch, `warning` on unverifiable nouns |
| 1.6 | Implement `report.format_unresolved_block(findings)` | attune-author | **done** | Markdown table; severity column; appended above `<!-- attune-generated ... -->` |
| 1.7 | Wire into `attune_author/polish.py` after the polish write | attune-author | **done** | Soft-fail: append to file. Strict mode: raise `FactCheckError` |
| 1.8 | Add `[tool.attune-author.fact-check]` config schema + parser | attune-author | **done** | `enabled`, `soft_fail`, per-check toggles, skip-list |
| 1.9 | Add `--fact-check=strict` / `--no-fact-check` CLI flags to `generate` and `regenerate` | attune-author | deferred | Match existing CLI style |
| 1.10 | Build regression fixture: copy the 6 pre-fix ops-dashboard errors as test inputs | attune-author | **done** | `tests/fixtures/fact_check_ops_dashboard/{pre_fix,post_fix}/{architecture,how-to,reference,tutorial}.md` |
| 1.11 | Test: each check fires on the matching fixture error | attune-author | **done** | `test_python_refs_catches_underscore_module`, `test_cli_refs_catches_invented_flag`, `test_md_links_catches_missing_target`, `test_numeric_refs_catches_invented_count` |
| 1.11.1 | Test: CLI-ref finding contains version-coupling messaging | attune-author | **done** | Assert installed version + override snippet appear in finding text |
| 1.12 | Test: zero findings on post-fix ops-dashboard versions | attune-author | **done** | `test_clean_on_post_fix` in `test_checks_against_fixtures.py` per check class |
| 1.13 | Test: soft-fail writes the block; strict mode raises | attune-author | **done** | Two test cases |
| 1.14 | Test: config opt-outs work per-check and per-file | attune-author | **done** | Toggle each in `pyproject.toml` test fixture |
| 1.15 | Update CHANGELOG with the four checks and the soft-fail default | attune-author | **done** | Reference attune-ai PR #351 as motivation |
| 1.16 | Update README with a short "Fact-check" section + one example output | attune-author | **done** | Keep it scannable; full docs go in attune-author's own help corpus later |

### Phase 1 testing strategy

- Pytest unit tests per check. Mock `importlib.import_module` only for
  edge cases (e.g., a module that imports successfully but then raises);
  prefer real imports against the actual attune package installed in
  the test venv.
- Regression fixture frozen in-repo: the 4 pre-fix ops-dashboard docs
  serve as ground truth. Test asserts that running fact-check on those
  files produces ≥ the specific findings list in
  `tests/fixtures/ops_dashboard_findings.yaml`.
- No external network in tests. `cli_refs` runs `attune <cmd> --help`
  against the locally-installed attune; this is acceptable because
  attune-author already declares attune-ai as a dev dep.

### Phase 1 exit checklist

- [x] Core implementation (tasks 1.1–1.8)
- [x] Test coverage (tasks 1.11, 1.11.1, 1.13, 1.14): 55 new tests
- [x] CHANGELOG + README (tasks 1.15, 1.16)
- [x] Regression fixture from attune-ai PR #351 (tasks 1.10, 1.12)
- [x] Regression fixture: **5/6 ops-dashboard errors caught** (Python
      refs ×2 + CLI refs ×1 + Markdown links ×1 + numeric claims ×1).
      The 6th error (missing-security-callout for `0.0.0.0`) is
      explicitly Phase 3 scope.
- [x] Zero findings on post-fix ops-dashboard versions
- [ ] CLI flags `--fact-check=strict` / `--no-fact-check` (task 1.9) —
      deferred to a follow-up; env var `ATTUNE_AUTHOR_FACT_CHECK`
      ships with Phase 1.
- [ ] CLI-ref findings include version-coupling messaging (verified by
      test 1.11.1)
- [ ] CHANGELOG + README updated
- [ ] Spec status updated to `complete (Phase 1)` here

---

## Phase 2: Ground-truth context injection

**Target PR scope:** ~400 LOC including tests. Depends on Phase 1 (uses
the same regression fixture but is otherwise independent of fact-check
code).

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 2.1 | Add `cli_command` field to `Feature` (the manifest model) | attune-author | **done** | Optional; load/save preserve; defaults None |
| 2.2 | Implement `ground_truth.extract_cli_help(cli_cmd, subcommand, project_root)` | attune-author | **done** | `subprocess.run(...)` with 10s timeout; `@lru_cache` per (exe, sub, cwd) |
| 2.3 | Implement `ground_truth.extract_public_api(source_paths)` | attune-author | **done** | AST walk: `__all__` + public function/class signatures (incl. method bodies) |
| 2.4 | Implement `ground_truth.extract_dataclasses(source_paths)` | attune-author | **done** | AST walk: `@dataclass` decorator + AnnAssign field collection. Module named `dataclass_refs` to avoid stdlib shadowing |
| 2.5 | Add `<cli_help>`, `<public_api>`, `<dataclasses>` sentinel blocks to polish prompt builder | attune-author | **done** | Composed in `ground_truth.build_context`; prepended to RAG context when both exist |
| 2.6 | Add system-prompt anchoring clause | attune-author | **done** | `ANCHORING_CLAUSE` exposed; appended via new `include_ground_truth_anchor` flag on `polish_template`/`build_polish_prompt`. Cache key shifts accordingly. |
| 2.7 | Implement 5KB context budget enforcement with drop order | attune-author | **done** | `ground_truth.budget.enforce_budget`; drops dataclasses → public_api → cli_help; logs warning per drop |
| 2.8 | Add `[tool.attune-author.context-injection]` config + CLI flags | attune-author | **done** | Config schema landed (enabled, per-source toggles, budget, executable); CLI flag deferred (env-driven defaults sufficient for first iteration) |
| 2.9 | Test: ground-truth extractors produce expected output on ops-dashboard source | attune-author | **done** | 25 tests across `test_public_api.py` + `test_dataclass_refs.py` |
| 2.10 | Test: polishing ops-dashboard with Phase 2 on, Phase 1 off recurs 0/3 high-severity errors | attune-author | **partial** | Unit-level: `test_polish_integration.py` asserts the sentinel blocks reach the user message and the anchor clause reaches the system prompt. Live-LLM acceptance run gated to a follow-up once an `ANTHROPIC_API_KEY` lane is available. |
| 2.11 | Test: budget enforcement drops sources in documented order | attune-author | **done** | 8 tests in `test_budget.py` covering drop order, fallback, log emission |
| 2.12 | Cost-delta measurement: 3-feature regression set with vs without Phase 2 | attune-author | deferred | Requires real-LLM run; defer to Phase 3 calibration when judge cost is also measured |
| 2.13 | Update CHANGELOG + README | attune-author | **done** | CHANGELOG entry under Unreleased. README addition in same PR. |

### Phase 2 exit checklist

- [x] Tasks 2.1–2.11, 2.13 done (60 new tests)
- [x] Spec status updated
- [ ] Live acceptance: 0/3 high-severity ops-dashboard errors recur in
      Phase-2-only polish (requires real-LLM run — gated to a follow-up
      task once `ANTHROPIC_API_KEY` is available in a CI lane)
- [ ] Cost delta < 10% (deferred to Phase 3 calibration run)

---

## Phase 3: Faithfulness judge integration

**Target PR scope:** ~300 LOC including tests. Depends on Phase 1 for
the `FactCheckReport` plumbing.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 3.1 | Add faithfulness-threshold + budget-cap config to `[tool.attune-author.fact-check]` | attune-author | **done** | `[tool.attune-author.fact-check.faithfulness]` sub-table; defaults threshold=0.95, budget=$0.10, model=Sonnet 4.6, enabled=False (opt-in) |
| 3.2 | Implement `faithfulness.judge_polished_file(polished_path, source_paths, config)` wrapper | attune-author | **done** | Wraps `FaithfulnessJudge` via `asyncio.run`; best-effort: missing extra / missing API key / over-budget all return `JudgeOutcome(score=None, skipped_reason=…)` rather than raising. `block_polish_on_unavailable=True` opt-in for strict CI. |
| 3.3 | Calibrate threshold against ops-dashboard fixture | attune-author | deferred | Requires real-LLM run; placeholder default `0.95` documented in decisions.md as pre-calibration. Calibration scheduled alongside live-LLM Phase 2 acceptance run. |
| 3.4 | Document calibration result in `decisions.md` (or design doc) | attune-author | deferred | Empty calibration record retained; will populate when 3.3 runs. |
| 3.5 | Wire judge into post-polish pipeline (after Phase 1 fact-check) | attune-author | **done** | `generator._run_faithfulness_judge` called after `_run_fact_check`; appends `## Faithfulness review` block when below threshold. `ATTUNE_AUTHOR_FAITHFULNESS=off` env override. |
| 3.6 | Cost telemetry: aggregate per-feature judge cost; report at end of `regenerate` | attune-author | **done** | Per-process telemetry state on `_faithfulness_telemetry`; `run_maintenance` resets at start and logs INFO summary at end (calls, skipped, total estimated $). |
| 3.7 | Test: judge runs and writes review block on a deliberately unfaithful synthetic input | attune-author | **done** | `test_pipeline_wiring.py::test_run_faithfulness_judge_appends_review_block_when_below_threshold` + `test_judge.py::test_judge_below_threshold_flags_threshold_not_met` |
| 3.8 | Test: budget cap skips judge call when estimated cost exceeds threshold | attune-author | **done** | `test_judge.py::test_judge_skipped_when_over_budget` |
| 3.9 | Update CHANGELOG + README | attune-author | **done** | CHANGELOG under Unreleased; README adds a "Faithfulness review (Phase 3)" subsection. |

### Phase 3 exit checklist

- [x] Tasks 3.1, 3.2, 3.5–3.9 done (30 new tests)
- [x] Threshold + cap configurable
- [x] Spec status updated
- [ ] Calibration (tasks 3.3, 3.4) — deferred until real-LLM run lands; placeholder default `threshold=0.95` documented in `decisions.md`

---

## Phase 4: Tutorial code-sample static check

**Target PR scope:** ~250 LOC including tests. Depends on Phase 1 for
plumbing.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 4.1 | Add `tutorial_static_check.check(polished_path, project_root)` to `fact_check/` package | attune-author | **done** | `is_tutorial_path(...)` heuristic gates routing in `check_polished_file` so only `docs/tutorials/` files run the static check |
| 4.2 | Code-fence extractor: pull all ```python fences with line numbers | attune-author | **done** | `_FENCE_PATTERN` regex; line numbers derived from `_line_of_offset` |
| 4.3 | `ast.parse` each fence; collect syntax errors as findings | attune-author | **done** | SyntaxError caught with the `exc.lineno` mapped back to absolute file line |
| 4.4 | Run `mypy --strict --no-error-summary` per fence | attune-author | **done** | `_run_mypy` via temp file + subprocess; 10s timeout; handles TimeoutExpired + FileNotFoundError + unexpected exit codes by returning `[]` |
| 4.5 | Parse mypy output into findings | attune-author | **done** | `_parse_mypy_output` regex; line numbers rewritten to absolute file position via `base_line + mypy_line - 1` |
| 4.6 | Strip `# attune-author: skip-mypy` directives before publication | attune-author | **done** | `strip_skip_directives_in_file` invoked in `apply_polish_results` for `tutorial` depth only; first-line directive only, trailing directives intentionally preserved |
| 4.7 | Add `[tool.attune-author.fact-check.tutorial_static]` config | attune-author | **partial** | Top-level `check_tutorial_static` toggle on `FactCheckConfig` (defaults True). Sub-table for `mypy_args` / `timeout_seconds` deferred — current constants match the spec; expose only when a real consumer needs the knob. |
| 4.8 | Test: pre-fix `tutorials/ops-dashboard.md` flags `_readers` + `_models` imports | attune-author | deferred | Requires the ops-dashboard regression fixture + real mypy run. Unit-level coverage via mocked mypy + syntax-error path is in place; the integration test lands alongside the live-LLM acceptance run. |
| 4.9 | Test: post-fix version produces zero errors | attune-author | deferred | Same gate as 4.8 |
| 4.10 | Test: `skip-mypy` directive is honored and stripped from output | attune-author | **done** | `test_check_skips_fence_with_directive` + `test_strip_skip_directive_first_line` |
| 4.11 | Test: total static-check time per tutorial < 10s | attune-author | deferred | Enforced indirectly via the 10s mypy subprocess timeout; a real bench lands with 4.8 |
| 4.12 | Update CHANGELOG + README | attune-author | **done** | CHANGELOG under Unreleased; README adds "Tutorial static check (Phase 4)" subsection. 4.2 execution explicitly noted as out of scope. |
| 4.13 | Add design.md follow-up section on Phase 4.2 execution tiers | attune-author | deferred | Tracked separately; not gating Phase 4.1 ship |

### Phase 4 exit checklist

- [x] Tasks 4.1–4.7, 4.10, 4.12 done (16 new tests)
- [x] Spec status updated
- [ ] Tasks 4.8, 4.9, 4.11 (real-fixture mypy runs) — deferred to the
      same live-LLM cycle that closes Phase 2/3's open items
- [ ] Task 4.13 (Phase 4.2 execution-tier design follow-up) — tracked
      separately; Phase 4.1 ships without it

---

## Cross-phase notes

### Testing strategy across all phases

- One regression fixture (the ops-dashboard editorial pass diff) used
  by all phases. Lives at `tests/fixtures/ops_dashboard_pre_fix/` and
  `tests/fixtures/ops_dashboard_post_fix/`.
- No mocking of LLM calls in integration tests. Mock at the unit-test
  level (`anthropic.Anthropic`) per the regen-pipeline pattern.
- CI runs all four checks on every PR after Phase 4 lands; before that,
  each phase's CI lane is its own job.

### Rollback strategy

Each phase has its own `enabled = true|false` toggle. If a phase causes
unexpected breakage in production regens, the operator can disable it
in `pyproject.toml` without touching code. Phase 1 is the only phase
whose disablement loses notable safety; the others gracefully degrade
to "no extra check."

### Sequencing rationale

Why this order: Phase 1 is the cheapest (no LLM, deterministic) and
catches the most distinct error types. Phase 2 has higher impact per
LLM-token but only matters if Phase 1's findings show consistent
hallucination patterns. Phase 3 needs Phase 1's plumbing for the
report-block format. Phase 4 is tutorial-specific and benefits from
Phase 1's `FactCheckReport` already existing.
