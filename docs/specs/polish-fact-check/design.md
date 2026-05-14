# Spec: Polish Fact-Check — Design

## Phase 2: Design

**Status**: draft

---

## Overall architecture

The four phases are independent layers stacked on the existing polish
pipeline. Each phase ships as its own PR and is opt-in via configuration
until Phase 4 (at which point all are on by default).

```
┌──────────────────────────────────────────────────────────────────┐
│  Existing polish pipeline (attune_author/polish.py)              │
│                                                                  │
│  source files ──► prompt builder ──► LLM ──► polished output     │
│                        ▲                          │              │
│                        │                          │              │
└──────────── Phase 2 ───┼──────────── Phase 1 ─────┼──────────────┘
                         │                          │
                         │                          ▼
              ┌──────────┴──────────┐    ┌──────────────────────┐
              │ Ground-truth        │    │ AST fact-check pass  │
              │ context injection   │    │ (post-generation)    │
              │   • CLI --help      │    │   • imports          │
              │   • __all__ list    │    │   • CLI flags        │
              │   • dataclass fields│    │   • md links         │
              └─────────────────────┘    │   • numeric claims*  │
                                          └──────────┬───────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────┐
                                          │ Phase 3: faithfulness│
                                          │ judge (attune-rag)   │
                                          └──────────┬───────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────┐
                                          │ Phase 4: static check│
                                          │ of tutorial samples  │
                                          │ (mypy + ast.parse)   │
                                          └──────────────────────┘

* Numeric-claim checking is Phase 1 stretch; documented but skippable.
```

---

## Phase 1 — AST-based post-generation fact-check

### Module layout

New module `src/attune_author/fact_check/` containing:

```
fact_check/
├── __init__.py       # public entry: check_polished_file(path, source_paths)
├── python_refs.py    # import-statement and dotted-path verification
├── cli_refs.py       # `attune <cmd> --flag` verification
├── md_links.py       # [label](target.md) target existence
└── report.py         # collect findings, format soft-fail block
```

### Public API

```python
def check_polished_file(
    polished_path: Path,
    source_paths: list[Path],
    *,
    project_root: Path,
    config: FactCheckConfig | None = None,
) -> FactCheckReport
```

- `polished_path` — the just-written polished markdown file
- `source_paths` — the source `.py` files the polish pass had as context
- `project_root` — used to resolve relative markdown links and run
  `<cmd> --help` invocations
- `config` — optional config; defaults come from `pyproject.toml`

Returns a `FactCheckReport` with a list of `Finding(severity, location,
message)` entries. The caller decides whether to soft-fail (append to
file) or strict-fail (raise).

### Check 1: Python imports and dotted-path references

For each Python code fence and inline `attune.X.Y` reference in the
polished file:

1. Extract import statements with `ast.parse` and walk the tree.
2. For each `from X import Y`, attempt `importlib.import_module(X)` in
   the active venv, then `getattr(module, Y)`. Failure = unresolved.
3. For each prose reference matching `attune\.[a-z_.]+\.[A-Za-z_]+`,
   resolve the full dotted path the same way.

Why import in the venv rather than parse-only: catches the
`attune.ops._readers` class of bug where the path *parses* fine but
doesn't actually exist. This was the most damaging failure mode in the
ops-dashboard fixture and parse-only AST won't catch it.

### Check 2: CLI flag references

For each `attune <subcommand> <flag>` pattern in the polished file:

1. Build a cache: for each subcommand referenced, run
   `attune <subcommand> --help` once and parse the output for flag
   names (regex: `--[a-z][a-z0-9-]*`).
2. For each `--flag` in the polished doc, confirm it appears in the
   cached help output for that subcommand.
3. Unknown subcommands are themselves a finding.

Cache scope: per-file, so a regen of one feature doesn't reinvoke
`--help` many times. Cache invalidation isn't needed (cache lives only
for the duration of the check call).

#### Version coupling — user-facing messaging

CLI-ref checks resolve against whatever `attune-ai` is installed in the
active venv. If a consumer is regenerating docs against a different
attune-ai version, false positives are possible. Every CLI-ref finding
includes proactive context so the user can resolve the ambiguity
without spelunking:

```
Line 17 (prose): `attune ops --read-only` — flag not found.

Detected against attune-ai 6.8.0 (installed in active venv). If you
are regenerating against a different attune-ai version, verify the
flag exists in that version's `attune ops --help`.

To override:
  - One-off:  attune-author generate FEATURE --skip-check cli_refs
  - Per file: [tool.attune-author.fact-check.skip]
              "docs/how-to/ops-dashboard.md" = ["check_cli_refs"]
```

The installed version is read from `attune.__version__` (or the
`importlib.metadata` fallback). If the consumer CLI isn't `attune` —
e.g. a third-party project using attune-author against its own CLI —
the same template renders with that project's CLI name and version.

### Check 3: Markdown link targets

For each `[label](path/to.md)` or `[label](path/to.md#anchor)`:

1. Resolve relative to `polished_path`'s directory.
2. Confirm the target file exists.
3. (Stretch: anchor existence by parsing target headers.)

External URLs (`http://...`, `https://...`) are skipped — not in scope.

### Check 4: Numeric claims

Promoted from stretch to required (per decisions.md). Catches the
`498 templates`-class of hallucination where the LLM invents a count
that has no source-of-truth.

For each sentence matching patterns like `\d+\s+(templates|features|workflows|skills|agents|workflows|tools|kinds)`:

1. Extract the noun and the count.
2. For nouns we can verify deterministically, count against the project
   filesystem:
   - `templates` → `find .help/templates -name "*.md" | wc -l`
   - `features` → number of top-level keys in `.help/features.yaml`
   - `workflows` → `list_workflows()` from the consumer's registry (if
     declared in `features.yaml`)
   - `kinds` → constant from attune-author (currently 11)
3. Severity: `error` if the doc's count doesn't match the verified count,
   `warning` if the noun isn't in the verifiable set (still surfaced for
   human review).

For nouns we *can't* verify (e.g., "thousands of LLM calls"), emit a
`warning` severity finding asking the human to confirm.

The exact noun-to-resolver mapping lives in
`fact_check/numeric_refs.py` and is extensible per consumer.

### Soft-fail output format

When findings exist, append to the polished file before the closing
`<!-- attune-generated ... -->` comment:

```markdown
## Unresolved references

> Auto-generated by attune-author fact-check. Review and either fix the
> source code, fix this doc, or add an override.

| Location | Severity | Issue |
|---|---|---|
| Line 77 (code fence) | error | `from attune.ops._readers import …` — module not found |
| Line 17 (prose) | error | `attune ops --allow-run` — flag not in `attune ops --help` |
| Line 124 (See also) | warning | `[Concept: Template design patterns](concepts/template-patterns.md)` — target file does not exist |
```

### Configuration

```toml
[tool.attune-author.fact-check]
enabled = true
soft_fail = true                    # false = raise on findings

check_python_refs = true
check_cli_refs = true
check_md_links = true
check_numeric_claims = false        # stretch; default off

# Per-file or per-feature opt-out
[tool.attune-author.fact-check.skip]
"docs/architecture/some-feature.md" = ["check_md_links"]
```

CLI overrides for one-off runs:

```bash
attune-author generate FEATURE --fact-check=strict
attune-author generate FEATURE --no-fact-check
```

### Phase 1 acceptance

1. `check_polished_file` exists, callable from a test.
2. Running it on the four ops-dashboard docs from attune-ai PR #351
   produces findings that match the editorial pass diff: **5 of the 6**
   errors fixed in `20438e8d` are flagged (Python refs ×2, CLI refs ×1,
   Markdown link ×1, numeric claim ×1). The 6th error
   (missing-security-callout for `0.0.0.0`) is explicitly Phase 3 scope.
3. Running it on the post-fix versions (current main of
   `feat/ops-dashboard-help-templates`) produces zero error-severity
   findings.
4. Soft-fail mode writes the unresolved-references block; strict mode
   raises `FactCheckError`.
5. Every CLI-ref finding includes the version-coupling messaging block
   (installed version + override snippet).

---

## Phase 2 — Ground-truth context injection

### Hook point

`attune_author/polish.py` builds prompts in `_build_polish_prompt` (or
equivalent — verified during implementation). Inject ground-truth
context as additional `<context>` blocks in the prompt before the
existing source-file block.

### Context sources

For a feature being polished:

1. **CLI help**: if `attune <subcommand>` is the consumer's CLI entry
   for this feature (configured per-feature in `features.yaml` as
   `cli_command: ops`), run `<consumer-cli> <subcommand> --help` once
   and inject the full output under a `<cli_help>` sentinel tag.
2. **Public API**: for each source `.py` file, extract `__all__` (if
   defined) and the signatures of public functions/classes (no
   underscore prefix). Inject under a `<public_api>` sentinel.
3. **Dataclass fields**: for any `@dataclass` in the source files,
   extract field names and types. Inject under a `<dataclasses>`
   sentinel.

### Prompt anchoring

Add a system-prompt clause (per the existing attune-rag
citation-forced-prompting pattern):

> The following context blocks contain **ground-truth surface details**
> for this feature. When you reference a CLI flag, public function,
> import path, or dataclass field, it MUST appear verbatim in the
> matching context block. If you need to describe something that isn't
> in the ground truth, describe the behavior without inventing a
> specific name.

### Context budget

Cap injected context at 5KB total (configurable). Measured against the
ops-dashboard fixture: rendered `--help` is ~1.5KB, `__all__` + signatures
is ~2-3KB, dataclasses ~1KB. Fits comfortably.

If budget exceeded, drop in this order: dataclasses → public API
signatures → `--help`. Drop with a log warning so the operator sees it.

### Phase 2 acceptance

1. Polishing `ops-dashboard` with Phase 2 enabled and Phase 1 disabled
   produces docs where 0 of the 3 high-severity errors from the fixture
   recur (CLI flag, private imports, route paths).
2. Total polish cost increases by less than 10% on average across the
   regression fixture (3 features).
3. Context-budget violations log a warning but don't fail the polish.

---

## Phase 3 — Faithfulness judge

### Integration point

attune-author depends on attune-rag (already; see
`pyproject.toml`). Import `attune_rag.eval.faithfulness.FaithfulnessJudge`
and wrap as a polish-pipeline post-step.

```python
from attune_rag.eval.faithfulness import FaithfulnessJudge

judge = FaithfulnessJudge(model="claude-haiku-4-5-20251001")
result = judge.score(
    answer=polished_text,
    sources=[src.read_text() for src in source_paths],
)
if result.mean_score < config.faithfulness_threshold:
    # Append review block to file; do not block commit
    ...
```

### Threshold calibration

Before defaulting, run the judge against:

- The pre-Phase-1 ops-dashboard fixture (6 errors): mean score should
  be < 0.9.
- The post-fix versions (after `20438e8d`): mean score should be ≥ 0.95.

If those two don't bracket cleanly, raise the threshold or tune the
prompt before defaulting.

### Budget cap

Estimated cost per file: ~$0.01-0.05 on Haiku 4.5. Per-feature
(11 kinds): ~$0.11-0.55. Per full regen (9 features): ~$1-5.

Hard cap: skip the judge call if estimated cost exceeds $0.10 for a
single feature. The cap is configurable.

### Phase 3 acceptance

1. Judge runs on every polished file and writes a `## Faithfulness
   review` block when mean score is below threshold.
2. Cost telemetry is reported at the end of each `attune-author
   regenerate` run.
3. Threshold is configurable in `pyproject.toml` and via CLI flag.

---

## Phase 4 — Tutorial code-sample static check

### Scope

Only `docs/tutorials/<feature>.md` files generated by attune-author. Other
docs (how-to, reference, architecture) may have code samples but
tutorials are where reader follow-along expectations are highest.

### Static check pipeline

For each polished tutorial:

1. Extract all ` ```python ` fences.
2. For each fence:
   a. `ast.parse(code)` — must succeed (syntax check).
   b. Write to a temp file; run `mypy --strict --no-error-summary` with
      attune installed in the active venv.
   c. Collect failures into `FactCheckReport` findings with severity
      `error` (mypy errors) or `warning` (mypy notes).

### Sample opt-out

For samples that intentionally use unresolved types (e.g., illustrative
pseudocode), add frontmatter inside the fence:

```python
# attune-author: skip-mypy
some_function_we_havent_built_yet()
```

The line is stripped before publication.

### No execution in Phase 4.1

Explicit non-goal: Phase 4.1 does **not** execute any sample. Reasoning
documented in the requirements doc (security + performance).

### Phase 4 acceptance

1. Running on the pre-edit tutorial `docs/tutorials/ops-dashboard.md`
   flags both `_readers` and `_models` imports (mypy will report them
   as unresolved imports against the installed `attune` package).
2. Running on the post-edit version produces zero errors.
3. Static check time per tutorial < 10s.

---

## Open design questions (resolve before Phase 1 implementation)

1. **`pyproject.toml` vs `.attune-author.toml`**: the regen-pipeline spec
   uses env vars; we should match its config-file convention if one
   exists. Confirm during Phase 1 task #1.
2. **Import resolution in the venv**: `importlib.import_module` against
   the active venv works but couples the check to whichever attune-ai
   version is installed. If a consumer is regenerating against an older
   attune-ai, false negatives are possible. Acceptable tradeoff;
   document.
3. **Phase 2 prompt-budget measurement**: do we measure context size in
   characters, tokens, or both? Tokens are more accurate but require
   running tokenizer. Start with characters; add tokenizer if drift
   suggests it.
