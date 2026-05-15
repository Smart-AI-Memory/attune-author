# Spec: Polish Fact-Check — Tasks

## Phase 3: Tasks

**Status**: draft

> Four phases, each shipping as its own PR. Phase 1 is the recommended
> first commitment; Phases 2–4 build on it. Phase 1 can be approved and
> shipped independently of Phases 2–4.

---

## Phase 1: AST-based post-generation fact-check

**Target PR scope:** ~600 LOC including tests.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 1.1 | Decide config-file location (`pyproject.toml` vs new `.attune-author.toml`) | attune-author | todo | Match regen-pipeline convention; document decision in PR |
| 1.2 | Create `src/attune_author/fact_check/` package skeleton with `__init__.py`, `python_refs.py`, `cli_refs.py`, `md_links.py`, `numeric_refs.py`, `report.py` | attune-author | todo | One module per check + shared `FactCheckReport` dataclass |
| 1.3 | Implement `python_refs.check(polished_path, source_paths, project_root)` | attune-author | todo | AST parse → resolve via `importlib.import_module` in active venv |
| 1.4 | Implement `cli_refs.check(polished_path, project_root)` | attune-author | todo | Per-file cache of `attune <cmd> --help` output; regex extract flag names. **Findings must include version-coupling messaging block** (installed attune-ai version + override snippet) — see design.md |
| 1.5 | Implement `md_links.check(polished_path, project_root)` | attune-author | todo | Resolve relative links; confirm target file exists |
| 1.5.1 | Implement `numeric_refs.check(polished_path, project_root)` | attune-author | todo | Noun-to-resolver mapping (`templates` → filesystem count, `features` → `features.yaml` key count, etc.). Severity: `error` on mismatch, `warning` on unverifiable nouns |
| 1.6 | Implement `report.format_unresolved_block(findings)` | attune-author | todo | Markdown table; severity column; appended above `<!-- attune-generated ... -->` |
| 1.7 | Wire into `attune_author/polish.py` after the polish write | attune-author | todo | Soft-fail: append to file. Strict mode: raise `FactCheckError` |
| 1.8 | Add `[tool.attune-author.fact-check]` config schema + parser | attune-author | todo | `enabled`, `soft_fail`, per-check toggles, skip-list |
| 1.9 | Add `--fact-check=strict` / `--no-fact-check` CLI flags to `generate` and `regenerate` | attune-author | todo | Match existing CLI style |
| 1.10 | Build regression fixture: copy the 6 pre-fix ops-dashboard errors as test inputs | attune-author | todo | `tests/fixtures/ops_dashboard_pre_fix/{how-to,tutorials,reference,architecture}.md` |
| 1.11 | Test: each check fires on the matching fixture error | attune-author | todo | `test_python_refs_catches_underscore_module`, `test_cli_refs_catches_invented_flag`, `test_md_links_catches_missing_target`, `test_numeric_refs_catches_invented_count` |
| 1.11.1 | Test: CLI-ref finding contains version-coupling messaging | attune-author | todo | Assert installed version + override snippet appear in finding text |
| 1.12 | Test: zero findings on post-fix ops-dashboard versions | attune-author | todo | Pull from attune-ai PR #351 head |
| 1.13 | Test: soft-fail writes the block; strict mode raises | attune-author | todo | Two test cases |
| 1.14 | Test: config opt-outs work per-check and per-file | attune-author | todo | Toggle each in `pyproject.toml` test fixture |
| 1.15 | Update CHANGELOG with the four checks and the soft-fail default | attune-author | todo | Reference attune-ai PR #351 as motivation |
| 1.16 | Update README with a short "Fact-check" section + one example output | attune-author | todo | Keep it scannable; full docs go in attune-author's own help corpus later |

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

- [ ] All tasks 1.1–1.16 done
- [ ] CI green
- [ ] Regression fixture: **5/6 ops-dashboard errors caught** (Python
      refs ×2 + CLI refs ×1 + Markdown links ×1 + numeric claims ×1).
      The 6th error (missing-security-callout for `0.0.0.0`) is
      explicitly Phase 3 scope.
- [ ] Zero findings on post-fix ops-dashboard versions
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
| 2.1 | Add `cli_command` field to `Feature` (the manifest model) | attune-author | todo | Optional; absence skips CLI-help injection |
| 2.2 | Implement `ground_truth.extract_cli_help(cli_cmd, subcommand, project_root)` | attune-author | todo | `subprocess.run(...)` with timeout; cache per (cmd, subcommand) pair |
| 2.3 | Implement `ground_truth.extract_public_api(source_paths)` | attune-author | todo | AST-walk for `__all__` + non-underscore-prefixed defs |
| 2.4 | Implement `ground_truth.extract_dataclasses(source_paths)` | attune-author | todo | AST-walk for `@dataclass`; collect field names + type strings |
| 2.5 | Add `<cli_help>`, `<public_api>`, `<dataclasses>` sentinel blocks to polish prompt builder | attune-author | todo | Match existing context-block format |
| 2.6 | Add system-prompt anchoring clause | attune-author | todo | "Ground-truth context blocks contain surface details — names you use must appear verbatim" |
| 2.7 | Implement 5KB context budget enforcement with drop order | attune-author | todo | Log warning on drop; never fail |
| 2.8 | Add `[tool.attune-author.context-injection]` config + CLI flags | attune-author | todo | Defaults: all three sources on, 5KB budget |
| 2.9 | Test: ground-truth extractors produce expected output on ops-dashboard source | attune-author | todo | Snapshot tests |
| 2.10 | Test: polishing ops-dashboard with Phase 2 on, Phase 1 off recurs 0/3 high-severity errors | attune-author | todo | The acceptance gate from `design.md` |
| 2.11 | Test: budget enforcement drops sources in documented order | attune-author | todo | Artificial 1KB cap forces drops |
| 2.12 | Cost-delta measurement: 3-feature regression set with vs without Phase 2 | attune-author | todo | Record in CHANGELOG; should be < 10% |
| 2.13 | Update CHANGELOG + README | attune-author | todo | |

### Phase 2 exit checklist

- [ ] Tasks 2.1–2.13 done
- [ ] 0/3 high-severity ops-dashboard errors recur in Phase-2-only polish
- [ ] Cost delta < 10%
- [ ] Spec status updated

---

## Phase 3: Faithfulness judge integration

**Target PR scope:** ~300 LOC including tests. Depends on Phase 1 for
the `FactCheckReport` plumbing.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 3.1 | Add faithfulness-threshold + budget-cap config to `[tool.attune-author.fact-check]` | attune-author | todo | Default threshold `0.95`; default cap `$0.10/feature` |
| 3.2 | Implement `faithfulness.judge_polished_file(polished_path, source_paths, config)` wrapper | attune-author | todo | Wraps `attune_rag.eval.faithfulness.FaithfulnessJudge` |
| 3.3 | Calibrate threshold against ops-dashboard fixture | attune-author | todo | Pre-fix should score < 0.9 mean; post-fix ≥ 0.95 |
| 3.4 | Document calibration result in `decisions.md` (or design doc) | attune-author | todo | Pre-committed matrix entry; concrete numbers |
| 3.5 | Wire judge into post-polish pipeline (after Phase 1 fact-check) | attune-author | todo | Append `## Faithfulness review` block when below threshold |
| 3.6 | Cost telemetry: aggregate per-feature judge cost; report at end of `regenerate` | attune-author | todo | Use existing telemetry hooks if any; otherwise log |
| 3.7 | Test: judge runs and writes review block on a deliberately unfaithful synthetic input | attune-author | todo | Construct a polished file that contradicts the source |
| 3.8 | Test: budget cap skips judge call when estimated cost exceeds threshold | attune-author | todo | |
| 3.9 | Update CHANGELOG + README | attune-author | todo | |

### Phase 3 exit checklist

- [ ] Tasks 3.1–3.9 done
- [ ] Calibration shows clean separation between pre-fix and post-fix
      fixture scores
- [ ] Threshold + cap configurable
- [ ] Spec status updated

---

## Phase 4: Tutorial code-sample static check

**Target PR scope:** ~250 LOC including tests. Depends on Phase 1 for
plumbing.

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 4.1 | Add `tutorial_static_check.check(polished_path, project_root)` to `fact_check/` package | attune-author | todo | Operates only on `docs/tutorials/*.md` |
| 4.2 | Code-fence extractor: pull all ```python fences with line numbers | attune-author | todo | Skip fences with `# attune-author: skip-mypy` first line |
| 4.3 | `ast.parse` each fence; collect syntax errors as findings | attune-author | todo | Cheap pre-check before invoking mypy |
| 4.4 | Run `mypy --strict --no-error-summary` per fence | attune-author | todo | Subprocess; timeout 10s; capture stderr |
| 4.5 | Parse mypy output into findings | attune-author | todo | Map line numbers back to original fence position |
| 4.6 | Strip `# attune-author: skip-mypy` directives before publication | attune-author | todo | Apply only to the file written; preserve in source if any |
| 4.7 | Add `[tool.attune-author.fact-check.tutorial_static]` config | attune-author | todo | `enabled`, `mypy_args`, `timeout_seconds` |
| 4.8 | Test: pre-fix `tutorials/ops-dashboard.md` flags `_readers` + `_models` imports | attune-author | todo | The headline acceptance gate |
| 4.9 | Test: post-fix version produces zero errors | attune-author | todo | |
| 4.10 | Test: `skip-mypy` directive is honored and stripped from output | attune-author | todo | |
| 4.11 | Test: total static-check time per tutorial < 10s | attune-author | todo | Bench against the ops-dashboard tutorial |
| 4.12 | Update CHANGELOG + README | attune-author | todo | Note Phase 4.2 (execution) explicitly deferred |
| 4.13 | Add design.md follow-up section on Phase 4.2 execution tiers | attune-author | todo | Reference the security + perf walkthrough from spec discussion |

### Phase 4 exit checklist

- [ ] Tasks 4.1–4.13 done
- [ ] Pre-fix fixture flagged correctly; post-fix clean
- [ ] Per-tutorial check time < 10s
- [ ] Spec status updated; full umbrella spec marked `complete`

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
