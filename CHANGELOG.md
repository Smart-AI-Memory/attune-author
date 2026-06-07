# Changelog

All notable changes to attune-author are documented in this
file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Polish prompt-cache hit-rate telemetry.** Each polish run now
  tracks Anthropic prompt-cache token usage and logs a one-line
  summary at the end of `attune-author regenerate`:
  `Polish cache hit: 87% (1241 read / 1421 total tokens, 6 call(s))`.
  A `WARNING` is appended when the run's hit rate falls below 50%,
  surfacing silent cache regressions (prompt edits, model alias
  drift). Hit rate is `read / (read + creation)` cacheable input
  tokens.
  - `attune_author.doc_gen._anthropic.call_anthropic` gains an optional
    `on_cache_usage(creation, read, model)` callback; backward
    compatible (the doc-gen path passes nothing).
  - New in `attune_author.polish`: `PolishCacheStats`,
    `polish_cache_stats()`, `format_polish_cache_summary()`,
    `reset_polish_cache_telemetry()`. Telemetry follows the existing
    in-process faithfulness-counter pattern (no new on-disk format).
  - README: new "Cache hit rate" subsection under Polish cache.
  - 16 new tests in `tests/unit/test_polish_cache_metrics.py`.

## [0.14.2] - 2026-05-27

### Fixed

- **Source-hash LLM laundering: features stay stale after a
  successful regen** ([#48](https://github.com/Smart-AI-Memory/attune-author/pull/48)).
  The polish LLM was given the rendered template (with
  frontmatter) as input context and asked to improve the body.
  Empirically, the LLM also echoed the frontmatter in its
  output — sometimes with single-character transcription errors
  in deterministic fields like `source_hash`. That broke
  staleness detection: the frontmatter `source_hash` written
  into the polished file didn't match what `compute_source_hash`
  recomputed on the same source, leaving the feature permanently
  "stale" after a successful regen.

  Concrete evidence from attune-ai's spec-engine feature
  (2026-05-27):

  ```
  frontmatter: f8ced22b02899aa25ff409636e659830c6ba856d70de6ddd1a9bf1cbe37a1337
  computed:    f8ced22b02899aa25ff709636e659830c6ba856d70de6ddd1a9bf1cbe37a1337
                                   ^
                                   position 19: LLM wrote f4 instead of f7
  ```

  Fix: field-level frontmatter merge in
  `generator.apply_polish_results`. The canonical value for
  every DETERMINISTIC field (`type`, `name`, `feature`, `depth`,
  `generated_at`, `source_hash`, `status`) is re-injected from
  the rendered template after polish, overriding whatever the
  LLM emitted. NON-deterministic fields (`polish: skipped`
  marker from the lenient-mode fallback path, any future
  polish-layer metadata) are preserved unchanged.

  Unblocks attune-gui Phase 2 (`living-docs-regen-automation`)
  which needed `attune-author status --dry-run` to reach a fixed
  point after regen. Once attune-gui pins this release, its CI
  `fail-if-stale` gate can be turned on. attune-ai's dashboard
  stale count also stops mis-flagging features that have just
  been regenerated.

  End-to-end verified: regenerating `spec-engine` on attune-ai
  with the fix in place produces 11 templates whose frontmatter
  `source_hash` all match `compute_source_hash`'s recomputed
  value (vs. 0/11 pre-fix).

### Changed

- **`publish.yml` trigger swapped from `release: [published]` to
  `push: tags: 'v*.*.*'`.** Aligns with the `publish-pypi.yml`
  pattern in attune-ai (synced 2026-05-25; original swap in
  attune-ai PR #459). Releases created by `GITHUB_TOKEN` (i.e.
  by another workflow) do NOT fire the `release:[published]`
  event — a documented GitHub Actions limitation that bit
  attune-ai's v7.1.0 ship. Tag-push fires unconditionally, so
  the publish workflow runs whether the release object was
  created by `gh release create` (human flow we use today), a
  release-automation workflow (future), or just `git push origin
  <tag>` without any release object at all. `workflow_dispatch`
  retained as fallback. No public API or package surface
  affected — this is CI hygiene.

## [0.14.1] - 2026-05-25

### Changed

- **Widen `attune-rag` pin in the `[rag]` extra: `>=0.1.0,<0.2`
  → `>=0.1.0,<0.3`.** Unblocks installs of `attune-author[rag]`
  alongside the freshly-released
  [attune-rag 0.2.0](https://pypi.org/project/attune-rag/0.2.0/),
  which is the first SemVer-binding cut. The 0.2.0 release is
  purely additive (new `attune_rag.measure_corpus` public module,
  new `load_aliases_from_file` helper, new
  `DirectoryCorpus(extra_aliases_file=...)` kwarg); the
  `RagPipeline` / `DirectoryCorpus` / `FaithfulnessJudge` APIs
  consumed by `attune_author.rag_hook` and `attune_author.faithfulness`
  are unchanged, so no code adaptation needed. Cap raised one
  minor (`<0.3`) rather than open-ended so the next breaking
  attune-rag bump still requires explicit re-validation.

## [0.14.0] - 2026-05-22

### Added

- **`check_workspace_staleness` public helper.** New convenience
  wrapper that takes a workspace path, locates `.help/` under it,
  loads the manifest, and runs `check_staleness` — returning an
  empty `StalenessReport` when no manifest is present. Lets
  downstream tools (attune-gui, future CLIs) ask "is this
  workspace's templates stale?" without duplicating the
  manifest-load + `.help/` convention. The underlying
  `check_staleness` API is unchanged. Exported from
  `attune_author` top-level. Also fixes the stale
  `__version__` string in `__init__.py` (was pinned at `0.11.1`
  through the 0.12/0.13 releases).

- **Polish fact-check Phase 4 — tutorial code-fence static
  check.** Polished tutorials (`docs/tutorials/*.md`) now have
  their ```python code fences extracted, syntax-checked with
  `ast.parse`, and type-checked with `mypy --strict` as a
  subprocess per fence. Failures land in the same
  `## Unresolved references` block as Phase 1 findings. The
  static check only runs on the tutorial doc kind — other kinds
  (how-to, reference, architecture) are skipped.
  - New module: `src/attune_author/fact_check/tutorial_static_check.py`.
  - `# attune-author: skip-mypy` as the first line of a fence
    opts that fence out of the mypy pass and is stripped from
    the published tutorial. Trailing directives are preserved
    (only first-line is recognized).
  - Subprocess robustness: missing `mypy`, 10-second timeout,
    and unexpected exit codes all degrade silently. The check
    never blocks the polish pipeline.
  - Config: `check_tutorial_static` toggle on
    `FactCheckConfig` (defaults `True`); routes only when the
    polished path lives under `tutorials/`.
  - 16 new tests under `tests/unit/fact_check/test_tutorial_static_check.py`.
  - Phase 4.2 (sample *execution* — running the code, not just
    type-checking it) is explicitly **out of scope** for this
    PR. Static check ships now; execution-tier design is
    deferred per the spec.

- **Polish fact-check Phase 3 — faithfulness judge.** Wraps
  `attune_rag.eval.faithfulness.FaithfulnessJudge` as a
  post-polish step: scores each polished file's claims against
  the source files it was generated from. When the score falls
  below the configured threshold, appends a
  `## Faithfulness review` block listing the unsupported claims
  and the judge's reasoning. Best-effort: missing
  `attune-rag[claude]`, missing `ANTHROPIC_API_KEY`, over-budget
  estimates, and transient API failures all degrade silently
  rather than blocking the polish.
  - New package: `src/attune_author/faithfulness/` with the
    judge wrapper, `FaithfulnessConfig`, `JudgeOutcome`,
    `estimate_cost_usd` budget-gate helper, and a
    `format_review_block` / `apply_review_block` soft-fail pair
    that mirrors the Phase 1 `## Unresolved references` shape.
  - Config schema:
    `[tool.attune-author.fact-check.faithfulness]` with
    `enabled`, `threshold` (default 0.95, pre-calibration), `budget_per_file_usd`
    (default $0.10), `model` (default Sonnet 4.6 — Haiku 4.5 is
    cheaper for high-volume runs), and
    `block_polish_on_unavailable` (default False — flip to True
    in CI where missing deps should be loud).
  - Cost telemetry: per-process counters on the generator
    module; `run_maintenance` resets them at start and logs an
    INFO summary at end with call count, skip count, and total
    estimated USD spent.
  - `ATTUNE_AUTHOR_FAITHFULNESS=off` env-var override for one-off
    disable without editing pyproject.
  - 30 new tests under `tests/unit/faithfulness/`.
  - Threshold calibration against the ops-dashboard fixture
    (tasks 3.3, 3.4) is **deferred** until the live-LLM Phase 2
    acceptance run; today's default of 0.95 is documented as
    pre-calibration in `decisions.md`.
  - Spec: `docs/specs/polish-fact-check/`. Phase 4 (tutorial
    code-fence mypy) remains on the roadmap.

- **Polish fact-check Phase 2 — ground-truth context
  injection.** Builds three sentinel-tagged blocks
  (`<cli_help>`, `<public_api>`, `<dataclasses>`) and injects
  them into the polish prompt above the existing source
  summary, with a short anchoring clause appended to the
  system prompt instructing the model to only reference names
  that appear verbatim in those blocks. Goal: prevent the
  six hallucination shapes documented in attune-ai PR #351's
  ops-dashboard editorial pass rather than catching them after
  the fact (Phase 1's job).
  - New package: `src/attune_author/ground_truth/` with
    `cli_help.py` (subprocess + LRU cache), `public_api.py`
    (AST walk for `__all__` + function/class signatures),
    `dataclass_refs.py` (AST walk for `@dataclass` field
    names/types), `budget.py` (5KB cap with documented drop
    order: dataclasses → public_api → cli_help), and
    `config.py` (`[tool.attune-author.context-injection]`
    schema).
  - New `Feature.cli_command` field on the manifest model;
    legacy manifests without this field continue to load. Save
    omits the field when `None`.
  - `build_polish_prompt` (used by both the synchronous and
    batch paths) accepts a new `include_ground_truth_anchor`
    flag; when True, the anchoring clause is appended to the
    system prompt and the prompt cache key shifts accordingly.
  - 60 new tests under `tests/unit/ground_truth/`.
  - Spec: `docs/specs/polish-fact-check/`. Phase 3
    (faithfulness judge integration) and Phase 4 (tutorial
    code-fence mypy) remain on the roadmap.

## [0.13.0] - 2026-05-15

> **Note**: skipping `0.12.0`. The internal `release/v0.12.0`
> branch carried the polish fact-check Phase 1 work but was
> never published to PyPI. That work now ships in `0.13.0`
> alongside the reference-template regenerator fixes prompted
> by attune-rag d39e39d.

### Added

- **Polish bypass surfaced in YAML frontmatter
  ([#33](https://github.com/Smart-AI-Memory/attune-author/pull/33)).**
  When the polish pass falls back to returning raw Jinja
  content in lenient mode (no API key, swallowed LLM error),
  the rendered template now carries a `polish: skipped` line in
  its YAML frontmatter. Without this marker the bypass was
  structurally invisible — same headings, same frontmatter
  shape — so degraded output slipped through PR review (see
  attune-rag commit d39e39d). Helper is idempotent; non-YAML
  output (project-doc HTML-comment-footer templates) passes
  through unchanged.

- **Polish fact-check (Phase 1 of [polish-fact-check
  spec](docs/specs/polish-fact-check/)).** AST-based
  post-generation verification of every polished template.
  Four checks, no LLM cost:
  - `check_python_refs` — imports + dotted attune-paths
    resolved against the active venv via
    `importlib.import_module`. Catches the
    `attune.ops._readers` class of hallucination.
  - `check_cli_refs` — `attune <subcommand> --flag`
    references compared against cached `--help` output.
    Findings include version-coupling messaging so the
    operator knows which attune-ai version was probed.
  - `check_md_links` — relative `[label](target.md)` link
    targets verified for existence.
  - `check_numeric_refs` — counts (`N templates`,
    `N features`, `N kinds`) verified against the project
    filesystem / manifest.

  Wired into the polish pipeline at
  [`generator.apply_polish_results`](src/attune_author/generator.py).
  Defaults to **soft-fail**: findings are appended to the
  polished file as an `## Unresolved references` block.
  Strict mode raises `FactCheckError`. Control via three
  layers (each overriding the next):
  1. `ATTUNE_AUTHOR_FACT_CHECK` env var
     (`off | soft | strict`, default `soft`) — shell-level
     intent, wins over per-invocation flags.
  2. `--fact-check` / `--no-fact-check` flags on
     `generate` and `regenerate` — per-invocation
     override.
  3. `[tool.attune-author.fact-check]` table in
     `pyproject.toml` — project-level defaults, per-check
     toggles, per-file skip list.

  Regression fixture frozen at
  `tests/fixtures/fact_check_ops_dashboard/` (pre-fix
  and post-fix versions of the four ops-dashboard docs
  from attune-ai PR #351). The Phase 1 exit gate is
  "5/6 errors caught" — Python refs ×2, MD links ×4+,
  numeric ×1; the 6th (insecure-example detection) is
  Phase 3 scope. Motivated by attune-ai PR #351, where
  one feature regen produced six factual errors that
  needed a manual editorial pass — five of six are now
  caught automatically.

### Changed

- **Reference templates carry typed Parameters/Returns columns
  without depending on polish
  ([#31](https://github.com/Smart-AI-Memory/attune-author/pull/31),
  closes [#30](https://github.com/Smart-AI-Memory/attune-author/issues/30)).**
  The Jinja meta-template for `reference.md` previously emitted
  a 3-column table (`Function | Description | File`). The
  richer 4-column table (`Function | Parameters | Returns |
  Description | File`) was only produced when the LLM polish
  pass succeeded and synthesized it. A polish bypass made the
  structural data vanish. AST-derived parameter and return data
  now flows through Jinja directly, so the structural ceiling
  no longer depends on the LLM. The `feature.description` from
  `features.yaml` also lands directly under the title. Polish
  keeps its job (rewriting prose, smoothing tone) and is no
  longer load-bearing for typed data. Legacy callers that pass
  only `public_functions` (without `function_signatures`)
  continue to get the 3-column fallback.

- **Test fixture isolates the polish cache per session
  ([#32](https://github.com/Smart-AI-Memory/attune-author/pull/32)).**
  The autouse `_lenient_polish_by_default` fixture now redirects
  `ATTUNE_AUTHOR_POLISH_CACHE` to a per-session `tmp_path_factory`
  directory. Previously, every test shared the dev machine's real
  `~/.attune/polish_cache`, so a prior live regenerate run could
  populate it and cause golden-snapshot tests to silently observe
  LLM-rewritten content instead of the deterministic Jinja
  fallback — flaky between machines and between sessions on the
  same machine. CI was unaffected (no cache present), so the
  regression hid locally. Also hardens `delenv` with
  `raising=False` so the fixture doesn't break on hosts without
  `ANTHROPIC_API_KEY` set.

## [0.11.1] - 2026-05-08

### Changed

- **Polish model rename: `claude-sonnet-4-20250514` →
  `claude-sonnet-4-6`.** Anthropic deprecated the dated alias
  with EOL 2026-06-15; the V2/V3 verification probes on
  2026-05-08 surfaced the deprecation warning. Migrating to
  the family alias matches attune-rag's existing
  `ClaudeProvider.DEFAULT_MODEL` and tracks Anthropic's
  recommended migration path. Affected:
  - [`polish.py:_POLISH_MODEL`](src/attune_author/polish.py)
    — drives every polish call (synchronous + batch).
  - [`doc_gen/config.py:DocGenConfig.model`](src/attune_author/doc_gen/config.py)
    — drives `attune-author docs` generation.
- **One-time cold cache after upgrade.** `_POLISH_MODEL`
  participates in the polish cache key, so existing cached
  entries become orphaned (they remain on disk but never
  match the new key namespace). The first regen after
  upgrade is a cold-cache miss for every feature; subsequent
  regens behave normally. Existing 30-day TTL prune
  ([polish._cache_prune](src/attune_author/polish.py))
  reaps orphaned entries automatically.

### Added

- **Mocked smoke test** at `tests/test_polish_smoke.py`
  pinning the wire-level model name. Catches the next
  model-rename failure immediately, no API spend.

### Notes

- Users who want to reclaim disk space immediately rather
  than waiting for the TTL prune can run
  `attune-author cache clear` post-upgrade. **Optional** —
  the cache shrinks automatically over 30 days.

## [0.11.0] - 2026-05-08

### Added

- **`attune-author regenerate --batch`** — opt-in batch path
  that submits all polish requests for stale features as one
  Anthropic Message Batches API call (~50% cost vs per-call
  pricing). Detaches; results are spliced back into the help
  corpus by a follow-up `--resume` invocation.
  - Companion flags: `--resume` (poll + splice + write),
    `--status` (one-shot query, supports `--json`),
    `--cancel` (call SDK cancel + remove state file),
    `--force` (with `--batch`: overwrite an existing pending
    state file).
  - Argparse mutex enforces "exactly one batch-mode flag at a
    time"; `--force` and `--json` are modifiers.
  - Bare `regenerate` (no batch flags) prints a one-liner hint
    when a state file exists; never auto-resumes.
- **`attune_author.maintenance_batch`** — new module containing
  `submit_maintenance_batch`, `resume_maintenance_batch`,
  `status_maintenance_batch`, `cancel_maintenance_batch` plus
  the `BatchState` schema and `.help/.batch-state.json`
  read/write/delete helpers. Includes 29-day stale-state
  detection (Anthropic's batch retention window).
- **`attune_author.doc_gen._anthropic_batch`** — SDK wrapper
  module exposing `submit_batch` / `poll_batch` plus typed
  `BatchPolishRequest` / `BatchPolishResult` records and an
  adaptive `timeout_secs` helper. SIGINT during polling cancels
  the batch and re-raises.
- **`attune_author.polish.build_polish_prompt`** — extracted
  prompt-building helper. Both the synchronous path and the
  batch path call it so the wire-level prompts are byte-identical.
- **`attune_author.generator.prepare_polish_phase`** /
  **`apply_polish_results`** — extracted Phase 1 (render) and
  Phase 3 (write) helpers. The synchronous
  `generate_feature_templates` now calls them; the batch path
  uses them too. Single source of truth for rendering.
- **Docs**: `docs/regenerate-batch.md` covers when to use which
  path, fallback behavior, env-var overrides, cancel semantics,
  and stale-state recovery.
- Live integration test at `tests/integration/test_batch_live.py`,
  gated on both `ANTHROPIC_API_KEY` and `RUN_LIVE_BATCH=1`. Tagged
  `@pytest.mark.live`. Default-skipped; ~$0.02 per run.

### Changed

- **`generate_feature_templates`** internal layout: refactored
  to call the new `prepare_polish_phase` and `apply_polish_results`
  helpers. **No behavior change** for existing callers — same
  inputs produce byte-identical on-disk templates. Verified by
  the existing 152 polish tests + the new parity test in
  `tests/test_maintenance_batch.py`.

## [0.10.0] - 2026-05-08

### Added

- **`attune_author.skill_export`** — exporter that writes one
  Claude Code `SKILL.md` per concept template in an
  attune-help-compatible corpus. Frontmatter `name` is the
  canonical feature slug (with `tool-` / `task-` prefixes
  stripped for parity with `summaries.json`); `description`
  resolves through summaries.json → frontmatter → first-paragraph
  extraction → generic stub. Body is the concept template
  content. Per-feature output goes to
  `<output>/<feature>/SKILL.md`.
- **`attune-author export-skills`** CLI subcommand. Defaults
  to attune-help's bundled corpus (resolved via
  `attune_help.adapters.rag.AttuneHelpAdapter`); `--source`
  overrides for project-local templates. `--overwrite` replaces
  existing SKILL.md files; absent it skips them with a recorded
  reason.
- 18 new tests in `tests/test_skill_export.py` covering canonical
  slug stripping, first-paragraph extraction, summary lookup,
  fallback chain, edge cases (missing summaries.json, empty
  body, unsafe slug, overwrite semantics).

### Notes

- Exporting the bundled attune-help corpus today produces 43
  skills covering the documented attune-ai workflows. Skill
  consumers (Claude Code, the marketplace) can load these as
  native skills with description-driven triggering — the
  attune-help corpus becomes a *generator* for skills rather
  than a runtime competitor. Phase one of the
  attune-help-as-skill recommendation from the 2026-05-08
  enhancements briefing.

## [0.9.1] - 2026-05-08

### Added

- **`attune_author.orchestration.commands.help`** — owns three
  `help.*` commands: `lookup`, `search`, `list`. Phase D3 of the
  architecture-realignment spec. Importing the module registers
  all three specs.
- `help.lookup` walks progressive depth (concept → task → reference)
  the same way the gui executor did; `help.search` and `help.list`
  pass through to `attune_help.HelpEngine` unchanged.

### Notes

- attune-help is **not** a hard dep of attune-author. The executor
  lazy-imports `HelpEngine` and surfaces a clear `ValidationError`
  if attune-help is missing. Hosts that wire `help.*` into a job
  runner (currently only attune-gui) already declare attune-help.
  Adding it as a hard dep here would create a circular metadata
  edge with attune-help's transitional shim (which depends on
  attune-author until 2026-07-07).

## [0.9.0] - 2026-05-08

### Added

- **`attune_author.orchestration.commands.author`** — owns all six
  `author.*` commands: `init`, `status`, `maintain`, `lookup`,
  `regen`, `setup`. Phase D2 of the architecture-realignment spec;
  each executor previously lived inline in `attune_gui.commands`.
  Importing the module registers all six specs on the global
  registry.
- **`attune_author.orchestration._helpers.resolve_project_paths`** —
  shared helper used by `status`, `maintain`, `regen`, `setup` for
  resolving `(project_root, help_dir)` from args. Drops the
  workspace fallback the gui copy used to have — that fallback is
  a host concern, not the orchestration runtime's. Hosts that want
  workspace-driven defaults preprocess args before calling
  `run_command`.
- `author.maintain`, `author.regen`, `author.setup` now return
  `project_root` in their output so the host can invalidate any
  cached pipelines tied to it. The previous gui-internal call to
  `attune_gui.routes.rag.invalidate(project_root)` moves into the
  gui's specialized proxy dispatcher (attune-gui 0.6.1).

### Notes

- Version bumped 0.8.1 → 0.9.0 because the public registry surface
  changes meaningfully (six new registered commands) and the
  effective contract for some commands tightened (no implicit
  workspace fallback for path-taking commands).

## [0.8.1] - 2026-05-08

### Added

- **`attune_author.orchestration.commands.rag`** — owns the
  `rag.corpus-info` command. Phase D1 of the
  architecture-realignment spec; the executor previously lived
  inline in `attune_gui.commands` (closes the first leg of finding
  #2 / ADR-003). Importing the module registers the spec on the
  global registry. The executor builds its own
  :class:`attune_rag.RagPipeline` from a `project_path` arg rather
  than reaching into attune-gui's private pipeline cache, keeping
  the dependency edge running rag → author cleanly.
- Establishes the canonical layout for Phases D2 (`author.*`) and
  D3 (`help.*`) command moves: one file per namespace under
  `attune_author/orchestration/commands/`, register at import time,
  tests in `tests/test_orchestration_commands_<ns>.py`.

## [0.8.0] - 2026-05-08

### Added

- **`attune_author.orchestration` scaffold.** New public package
  exporting `run_command`, `list_commands`, `register`,
  `CommandSpec`, `JobContext`, `RunResult`, and the
  `OrchestrationError` family (`CommandNotFound`, `ValidationError`,
  `RunnerBusy`). Phase C of the architecture-realignment spec.
  The registry ships empty; Phases D1–D3 will move the existing
  commands in from `attune_gui.commands` so attune-gui shrinks to a
  thin route layer (closing finding #2 / ADR-003).
- `CommandSpec` is field-for-field compatible with attune-gui's
  current dataclass so the migration PRs are mechanical.

## [0.7.0] - 2026-05-08

### Changed

- **`attune_author.manifest` / `attune_author.staleness` /
  `attune_author.freshness` are now the source of truth.** These
  modules previously re-exported from `attune-help`; with PR #14
  they ship natively in attune-author. Existing imports from
  `attune_author.*` continue to work; downstream code using
  `attune_help.*` now goes through deprecation shims (see
  `attune-help` 0.11.0 CHANGELOG).

### Removed (dependency)

- **`attune-help>=0.10.0` runtime dependency dropped.** It was a
  leftover from when `manifest`/`staleness`/`freshness` lived in
  attune-help and this package re-exported them. After PR #14
  inverted the direction, no `from attune_help` imports remain in
  `src/attune_author/`. Removing the dep also breaks the circular
  package-metadata edge that would otherwise form once
  `attune-help` 0.11.0 declares `attune-author>=0.7.0`.

## [0.5.1] - 2026-04-30

### Changed

- **Staleness shim** — `attune_author.staleness` now re-exports
  `compute_semantic_hash` from `attune-help>=0.10.0`, which introduced
  Phase 1 semantic freshness hashing. No behaviour change for existing
  callers of `compute_source_hash` — the delegation is automatic.

## [0.5.0] - 2026-04-24

### Added — Project-doc generation (four new kinds that write to `docs/`)

- **`how-to`** — procedural guides for competent readers
  (quick-start, core API, integration patterns).
- **`tutorial`** — step-by-step learning content with
  prerequisites and verification.
- **`cli-reference`** — precise command reference
  (description, usage, options, exit codes).
- **`architecture`** — structural/design overview for
  engineers extending the subsystem.

Unlike `.help/` templates, project-doc kinds render without
YAML frontmatter. Staleness is tracked via an HTML comment
footer appended to the file, so the output renders cleanly
as plain markdown in a `docs/` tree:

    <!-- attune-generated: source_hash=<sha256> feature=<name>
         kind=<kind> generated_at=<YYYY-MM-DD> -->

Output paths: the generator respects `feature.doc_path` /
`feature.arch_path` from the manifest when set, otherwise
falls back to `docs/<subdir>/<feature-name>.md` (subdirs:
`how-to/`, `tutorials/`, `reference/`, `architecture/`).

`attune-author generate --all-kinds` now renders both the
`.help/` set and the four project-doc kinds in one call.

### Added — Polish prompts for the new kinds

Per-kind system prompts and anti-patterns in
`polish_prompts.py` for `how-to`, `tutorial`, `cli-reference`,
and `architecture`. Prompt guidance is distinctive enough
that the test suite asserts each kind carries a unique phrase
and lists its anti-patterns.

### Added — Validation hardening

- **Multi-path warning.** When `feature.doc_paths` has more
  than one entry, the generator logs a WARNING naming the
  ignored paths. Only `doc_paths[0]` is written in this
  release; multi-path generation is a planned follow-on.
  Additional paths are still tracked by `check_staleness`.
- **HTML-footer staleness round-trip tests.** New
  `tests/test_staleness.py::TestProjectDocFooterStaleness`
  exercises generator → `parse_doc_footer` →
  `check_staleness` end to end: fresh doc is current, source
  change flips it to stale, missing doc is stale.
- **Multi-path warning tests.** New
  `TestMultiDocPathWarning` asserts the warning fires for
  `doc_paths` with >1 entry and stays silent for 1.

### Changed

- **`attune-help` dep lower bound raised to `>=0.8.0`** so we
  can use the new `doc_paths` list, `arch_path`, `doc_kinds`,
  and `build_doc_footer` / `parse_doc_footer` helpers that
  landed in attune-help 0.8.0.
- **`StalenessReport`** now has separate `help_entries` and
  `doc_entries`. `format_status_report()` renders the two
  sections independently so users can see template vs. doc
  staleness at a glance.
- **Shim tightening.** `attune_author.staleness` and
  `attune_author.manifest` continue to re-export the shared
  implementations from `attune_help` so existing imports keep
  working.

### Docs

- README Roadmap and feature-matrix callouts updated to
  mention the `docs/` output alongside `.help/templates/`.

### Tests

- **497 tests pass** (6 new), ruff clean, mypy clean.

## [0.4.2] - 2026-04-19

### Changed

- **`rag_hook.ground_polish_context` now uses
  `RagResult.context` directly** instead of rebuilding the
  context block from citation hits via a corpus lookup.
  attune-rag 0.1.3+ exposes the pre-joined context on the
  result object; the old `_hits_from_citation` helper
  duplicated that logic and held a fragile dependency on
  `attune_rag.retrieval.RetrievalHit`,
  `attune_rag.prompts.join_context`, and the `pipeline.corpus`
  attribute. Deleting it removes 3 medium-risk rows from
  attune-author's attune-rag API surface — any future minor-
  version refactor of those internals no longer breaks the
  polish hook. The character budget for the polish context
  block is now pinned at 8 KB (was also 8 KB before, passed
  to `join_context(max_chars=...)`); changes that matter to
  polish cost stay visible as a module-level constant
  (`_POLISH_CONTEXT_MAX_CHARS`).

### Verified

- 497 tests pass, 31 skipped. `test_rag_hook.py`
  test_ground_polish_context_returns_markdown_when_hits
  updated to stage `result.context` directly (no more
  `pipeline.corpus.get` mock).

## [0.4.1] - 2026-04-19

### Changed

- **Upper cap on `attune-help` raised from `<0.6` to `<0.8`.**
  attune-help 0.7.0 is additive per its CHANGELOG (path-keyed
  summary sidecar, per-feature query fixtures, CLI, Beta
  classifier) — no API breaks. Bumping the cap unblocks
  attune-ai consumers that want to pull in both attune-rag
  0.1.4 (transitively requires `attune-help>=0.7.0`) and
  attune-author via a single extras install, without forcing
  attune-help back down to 0.5.x.

### Added

- **`--all-kinds` flag on `attune-author generate`.** By
  default the CLI produces the three core template depths
  (concept, task, reference). `--all-kinds` generates the
  full 11-kind surface (adds comparison, error, faq, note,
  quickstart, tip, troubleshooting, warning) so consumers
  that want uniform staleness tracking across every template
  kind can get it in one command. Previously only
  `scripts/regenerate_help.py` passed the full kind list.
- **`rag-hook` feature** in `.help/features.yaml` + 11
  polished templates covering the optional RAG-grounded
  polish path (`src/attune_author/rag_hook.py`). Dogfoods
  the new `--all-kinds` flag.

### Verified

- 497 tests pass / 31 skipped with attune-help upgraded
  from 0.5.1 to 0.7.0. No behavioral regressions, public
  API unchanged.

## [0.4.0] - 2026-04-18

### Added (0.4.0)

- **Optional RAG-grounded polish** — new `[rag]` extra
  (`pip install 'attune-author[rag]'`). When installed,
  the LLM polish pass consults existing attune-help
  templates via
  [attune-rag](https://github.com/Smart-AI-Memory/attune-rag)
  before rewriting, using hits as style and naming
  references. Off via `--no-rag` per invocation or
  `ATTUNE_AUTHOR_RAG=0` globally. Without the extra
  installed, behavior is unchanged.
- **`src/attune_author/rag_hook.py`** — new module
  exposing `rag_enabled()` and
  `ground_polish_context(feature_name, template_type, k)`.
  Lazy imports throughout; graceful degradation on any
  retrieval failure.

### Changed (0.4.0)

- **`polish_template()`** gains optional
  `augmented_context` kwarg. Injected into the LLM
  user_message between the feature intro and source-info
  sections. Existing callers unaffected.
- **`generate_feature_templates()`** gains
  `use_rag: bool = True` kwarg. Threads through
  `_maybe_polish()` to `rag_hook.ground_polish_context`.
- **`attune-author generate`** gains `--no-rag` flag.

### Safety (0.4.0)

- Injected retrieval context is framed with an explicit
  "Use as style reference — do NOT copy content or invent
  anything they don't attest" instruction as mild
  defense against prompt injection from retrieved content.
- Joined context capped at 8,000 characters to protect
  prompt budgets.
- All exception paths degrade to `None` + warning log
  rather than breaking generation.

### Tests (0.4.0)

- 10 new `tests/test_rag_hook.py` covering env-var gate,
  import gate, happy path with mocked `RagPipeline`,
  fallback path, exception recovery, and query shape.
  Full suite: 497 passed + 31 skipped (no regressions).

## [0.3.9] - 2026-04-14

### Changed (0.3.9)

- **Reference polish prompt — prose/table register split**
  — the reference system prompt now separates voice from
  facts explicitly. Prose sections (h1 subtitle, overview,
  description cells) follow Google developer documentation
  style with concrete-verb guidance; table columns other
  than `Description` hold Python identifiers, types, and
  source literals verbatim. Fixes the "stiff, dry" output
  readers reported without loosening any of the v0.3.8
  accuracy requirements (raises, literals, dataclass
  fields, properties, module constants).
- **`Raises` heading pinned literally** — the polish prompt
  now requires the exact word "Raises" (not "Exceptions",
  "Errors", or "Failure modes") for exception subsections
  and columns. Matches Python docstring convention
  (Google/NumPy/Sphinx) and restores the grep anchor
  readers expect.
- **Identifier column rule tightened** — prose-register
  license was leaking into the Constants table, causing
  the model to rewrite `_CORE_DEPTH_NAMES` as "Core depth
  names." Prompt now enumerates which columns are
  verbatim and scopes rephrasing to the `Description`
  column only.
- **Full corpus regenerated** — all 11 template kinds
  regenerated for every feature against the new prompt.
- **Version bump also catches `__init__.py`** from the
  stale 0.3.7 value left over from the v0.3.8 release.

### Benchmarked (0.3.9)

- v0.3.9 hallucination benchmark committed at
  `benchmarks/hallucination-v0.3.9/`, run against the
  final regenerated corpus. Zero hallucinations across
  100 answers (2 models × 2 conditions × 25 questions).
  Treated condition: opus 25/25 correct, sonnet 24/25
  correct + 1 judge-parse error on q30 (judge LLM failed
  to emit valid JSON on two retries; sonnet's answer was
  factually correct — listing the exact members of
  `_FALSY` — and the same question scored correct under
  v0.3.8's judge run with the same reference content).
  No factual regressions vs v0.3.8.

## [0.3.8] - 2026-04-14

### Added (0.3.8)

- **Diagnostic-stem extraction for `raises`** — the AST
  extractor now captures the literal exception message
  (e.g. `'Invalid feature name: {...}'`) alongside the
  exception class, so reference templates surface the
  grep-able error text users actually see when debugging.
  Handles plain string literals and f-strings (computed
  parts rendered as `{...}`). Same function raising the
  same class with different messages now yields one entry
  per distinct message.
- **Module-constants extraction** — module-level list /
  tuple / set literals of strings (e.g. `_FALSY`,
  `_UNSAFE_NAME_TOKENS`) are now extracted into
  `_SourceInfo.module_constants` and fed into the polish
  prompt. Reference pages render an Allowed-values / Constants
  table instead of summarizing the members in prose —
  underscore-prefixed names are rendered because what users
  need to know is the *values*, not the leading underscore.
- **`@property` extraction** — class-level `@property`
  accessors are extracted separately from methods so
  reference pages render a dedicated Properties table
  (`Property | Type | Description`, no parentheses) rather
  than misrepresenting them as zero-arg methods.
- **Literal return-data rendering for tool-schema factories**
  — functions that return a dict of descriptors (`get_tools`,
  any `get_commands`-shaped factory) have that structure
  rendered into the polish prompt as indented YAML-like text
  (8 KB cap), so reference pages present one sub-section
  per tool with Parameters / Fields tables instead of a
  generic "returns a dict" summary.
- **v0.3.8 hallucination benchmark** —
  `benchmarks/hallucination-v0.3.8/` with the full question /
  context / answer / judgment set against the current
  generator. `benchmarks/hallucination-v0.3.7/` archived
  for regression comparison.
- **Weekly cross-repo compat CI** — new
  `.github/workflows/cross-repo-compat.yml` installs
  attune-help from its `main` branch every Monday and runs
  this repo's test suite against it. First `tests`-style
  workflow in the repo; also triggerable on demand.

### Changed (0.3.8)

- **Polish prompt tightened around accuracy requirements**
  — explicit rules now require: Returns columns for any
  function with an annotated return type (full type
  preserved — no prose summaries of `tuple[str, list[str]]`);
  Parameters columns preserving defaults and `Literal[...]`
  enum values verbatim; Raises columns rendering the
  diagnostic stem when source info provides it; Fields
  tables for dataclasses; Properties tables for `@property`
  accessors; Constants / Allowed-values tables for
  module-level string collections. Closes the remaining
  hallucination gaps the v0.3.6 benchmark surfaced.
- **60+ reference / task / concept templates regenerated**
  under `.help/templates/**` against the grounded polish
  prompt and the new source extraction.
- **README rewritten** to lead with the dynamic,
  context-sensitive help framing — manifest-driven,
  source-hash-tracked, progressively-rendered help rather
  than a static docs generator. Feature list re-grouped
  around progressive depth, context-sensitive delivery,
  and grounded generation.
- **`attune-help` dependency upper-capped** — now
  `>=0.5.1,<0.6` (was `>=0.5.1`), with an inline comment
  documenting the schema-contract rationale
  (attune-author writes content that attune-help renders).
- **PyPI project URLs point to the extracted repo**
  (`Smart-AI-Memory/attune-author`) instead of the parent
  `attune-ai` monorepo. Added `Changelog` and `Issues`
  URLs.

### Tests (0.3.8)

- **Source-extractor coverage** — 273 new lines in
  `tests/test_source_extractors.py` covering the new
  raises-message, module-constants, and `@property`
  extraction paths, plus f-string message rendering and
  duplicate-pair collapsing.
- `tests/test_dogfood_help.py` updated to match the new
  source-info shape.

## [0.3.7] - 2026-04-14

### Added (0.3.7)

- **Source-grounded accuracy for reference templates** — the generator
  now extracts the `raises` list, `Literal[...]` allowed values, and
  dataclass field name/type/default tuples via AST and surfaces them
  to the polish prompt. The reference-template prompt treats them as
  required output (Parameters columns keep defaults, Raises columns
  name each exception, dataclass Fields tables replace prose). Closes
  the four hallucination gaps the v0.3.6 benchmark surfaced.
- **Consistent `init` hint across `status`, `regenerate`, and
  `generate`** — running any of these in a project without a manifest
  now prints the same "No manifest at .../.help/features.yaml. Run
  `attune-author init` first." message. Previously only `generate`
  guided the user; `status` and `regenerate` dead-ended with a
  terse "Error: No features.yaml in ...".
- **Manifest validation errors include the file path** — malformed
  `features.yaml` now reports `Invalid manifest at /path/to/.help/features.yaml:
  expected mapping, got str` instead of omitting the path, so users
  know which file to fix.
- **CLI subcommand descriptions and examples** — every subcommand now
  renders a description line when the user runs `--help`, flag help
  text includes `(default: ...)` via `%(default)s`, `--overwrite`
  explains what a manual template is, and the top-level parser has an
  epilog with four usage examples.
- **Git post-commit hook (`.githooks/post-commit`)** — after each
  commit the hook runs `run_hook()`, which diffs the last commit,
  matches touched files against feature globs, and regenerates only
  the affected templates. Activate with `git config core.hooksPath
  .githooks` or `make setup`.
- **`Makefile` for dev setup** — `make setup` configures git hooks
  and installs dev deps. `make status`, `make regenerate`, `make test`,
  `make lint` are convenience targets.

### Changed (0.3.7)

- **`author_generate` MCP tool returns a structured `available`
  field** — when the requested feature is not in the manifest, the
  error response now includes a separate `available: [...]` key
  instead of embedding the list inside the error string, matching
  the existing `author_lookup` pattern.
- **`author_maintain` wraps manifest errors with `Cannot load
  manifest:` prefix** — previously surfaced the raw exception text;
  now consistent with `author_status`, `author_generate`, and
  `author_lookup`.
- **Path-traversal error message reworded** — `Cannot access system
  directory: /etc` is now `Path is outside the project: /etc is a
  system directory`, which reads as a containment violation instead
  of a leaked internal error.

### Fixed (0.3.7)

- **`_extract_raises` now returns exceptions in source order** —
  the docstring promised source order but the implementation used
  `ast.walk` (BFS), so nested `raise` statements inside `if`/`try`
  blocks surfaced after later top-level raises. Switched to a
  pre-order DFS via `ast.iter_child_nodes`.
- **`__version__` no longer stale** — `src/attune_author/__init__.py`
  had been pinned at 0.3.3 across the 0.3.4/0.3.5/0.3.6 bumps, so
  `attune-author --version` reported the wrong number. Now synced
  with `pyproject.toml`.

### Tests (0.3.7)

- **`tests/test_source_extractors.py`** — 25 new unit tests covering
  the four AST extractors (`_extract_raises`, `_extract_literal_values`,
  `_extract_param_literals`, `_is_dataclass`, `_extract_dataclass_fields`).
- **Two new CLI tests** — `test_status_missing_manifest_hints_init`
  and `test_regenerate_missing_manifest_hints_init` lock in the
  unified init-hint behavior.

## [0.3.3] - 2026-04-11

### Added (0.3.3)

- **Context-aware welcome screen for bare `attune-author`** — running
  the CLI with no subcommand now prints a short welcome that adapts
  to the current directory. On a fresh project it tells the user
  the project isn't set up yet and points at `attune-author init`.
  On an initialized project it lists up to 8 feature names and
  suggests `status` or `generate <feature>`. A malformed manifest
  falls through to the "not set up yet" path so a cold invocation
  never surfaces a traceback. `--help` / `-h` still prints the full
  argparse reference.
- **Friendly usage hints when `generate` or `docs` are missing
  required args** — `attune-author generate` with no feature now
  lists the available features from the manifest (or points at
  `init` if there's no manifest), and `attune-author docs` with no
  target shows a usage hint with an example invocation and a
  reminder about the `[ai]` extra. These replace argparse's terse
  "the following arguments are required" errors.

### Changed (0.3.3)

- **`generate` error output goes to stderr** — the "feature not
  found in manifest" and "manifest missing" messages previously
  printed to stdout, making it hard to distinguish from normal
  output in shell pipelines. They now print to stderr where they
  belong.

## [0.3.2] - 2026-04-11

### Fixed (security) (0.3.2)

- **CLI path inputs now validated** — `attune-author init`, `status`,
  `generate`, `regenerate`, and `docs` previously resolved
  `--project-root`, `--help-dir`, the docs target, and `--output`
  with a bare `Path(...).resolve()`, skipping the null-byte and
  system-directory checks the MCP handlers already enforced. All
  CLI-user-controlled paths now route through
  `attune_author.mcp.path_validation.validate_file_path()`, so the
  CLI surface matches the MCP surface.

### Fixed (0.3.2)

- **`bootstrap._infer_description` module-docstring parsing** — the
  helper used manual triple-quote slicing that would latch onto any
  `"""` in the file, not just the module docstring, producing wrong
  or truncated descriptions when `__init__.py` contained in-body
  strings. It now parses the file with `ast.get_docstring(ast.parse(...))`
  and gracefully handles `SyntaxError`.

### Changed (0.3.2)

- **Internal: `generator._extract_source_info` refactored** — the
  function/class AST walk was split into `_docstring_first_line`,
  `_collect_function`, and `_collect_class` helpers to remove
  duplicated doc extraction and flatten the main loop. No API change.
- **Internal: `_format_function_signature` posonly guard simplified** —
  the redundant `arg is posonly[-1] and idx == len(posonly) - 1`
  check has been replaced with the sufficient index comparison.

### Tests (0.3.2)

- **`TestModuleGlue` added to `tests/test_mcp_server.py`** — 5 new
  tests cover `_get_app` singleton caching, `create_server`, and the
  `_handle_list_tools` / `_handle_call_tool` SDK adapter bodies,
  lifting `mcp/server.py` from 67% to 80% coverage and the project
  total from 89% to 90%.

## [0.3.1] - 2026-04-11

### Fixed (security) (0.3.1)

- **Path traversal via crafted feature name** — `manifest.load_manifest()`
  now rejects feature names containing `/`, `\`, `..`, or null bytes
  at parse time, closing a gap where a hand-edited `.help/features.yaml`
  could push an unsafe name into the `.help/templates/<name>/`
  directory join. Previously the guard existed in
  `generator.py` but not in the manifest loader, so callers reaching
  templates through `mcp.handlers.author_lookup()` could bypass it.
  The check is now centralized in
  `attune_author.manifest.is_safe_feature_name()` and reused by the
  generator, MCP `author_lookup` handler (defense in depth), preamble
  lookup, and staleness reader.
- **`author_docs` output-path validation ordering** — the MCP
  `author_docs` handler previously ran `mkdir(parents=True)` on the
  output parent **before** validating it against the workspace root,
  meaning a rejected path could still materialize a directory tree at
  an attacker-controlled location on disk. The handler now validates
  the parent first and only creates it after the workspace-containment
  check passes.

### Fixed (0.3.1)

- **Wheel packaging missed `_partials/` Jinja2 includes** — the
  `[tool.setuptools.package-data]` glob was `meta_templates/*.j2`,
  which does not recurse, so the `_partials/problem_macros.j2` macro
  file was excluded from built wheels and any template importing it
  would fail at runtime in installed environments. The glob is now
  `meta_templates/**/*.j2`.

### Changed (0.3.1)

- **Doc-gen system prompts moved out of `stages.py`** — the three
  stage prompts (outline, write, review) now live in a new
  `attune_author.doc_gen._prompts` module, mirroring the
  `polish_prompts` pattern. Each stage's "You are an expert technical
  writer" opening is shared via a single base constant so future tone
  changes only land in one place. No behavior change.
- **Lenient-mode polish failures now log at `error` level** instead
  of `warning`, so the user-visible degradation that lenient mode
  promises is actually visible in default log filters.
- **`generator._is_manual()` debug log on read failure** — silent
  `OSError -> False` now also emits a debug log so failed reads are
  diagnosable from logs alone.

### Added (0.3.1)

- **`attune_author.manifest.is_safe_feature_name()`** — public helper
  that any caller treating a feature name as a filesystem path
  component should use.
- **Test coverage** — 26 new tests covering: `is_safe_feature_name`
  parametrized happy/sad paths, manifest-load rejection of unsafe
  names, MCP handler error paths (missing manifest on three handlers,
  output-path escape rejection without leaving dirs on disk, pipeline
  RuntimeError surfacing), strict-mode polish behavior (missing key,
  LLM error, env-var default), and a new `test_polish_prompts.py`
  exercising `get_system_prompt()` for every registered template kind.
  Total suite: 343 passing (up from 317), coverage 89%.

## [0.3.0] - 2026-04-11

### Changed (breaking) (0.3.0)

- **Polish is now strict by default.** `polish_template()`
  previously fell back to the raw Jinja2 output on any
  failure (missing `ANTHROPIC_API_KEY`, network error,
  SDK error). As of this release, every such failure
  raises :class:`PolishError`. The rationale is that
  polish is load-bearing for output quality — silent
  fallback was letting inferior templates ship unnoticed.
  **Migration:** environments that genuinely cannot run
  the LLM pass (CI without credentials, tests, offline
  dev boxes) must opt out explicitly via either
  `polish_template(..., strict=False)` or by setting
  the environment variable
  `ATTUNE_AUTHOR_STRICT_POLISH=false`. The env var
  semantics are inverted from 0.2.0: unset, truthy, and
  unrecognized values all mean "strict" now; only the
  known falsy tokens (`0`, `false`, `no`, `off`) disable
  strict mode.

### Added (0.3.0)

- **Shared Anthropic call helper** — new
  `attune_author.doc_gen._anthropic` module centralizes
  client construction, single-turn `messages.create()`
  invocation, and error wrapping for every code path
  that touches the Anthropic SDK. A single redaction
  pass strips anything matching `sk-ant-...` from
  exception text and the error is re-raised with
  `from None` so API keys cannot leak through
  `str(exc.__cause__)`. The doc-gen stages and
  `polish._call_llm()` both delegate to it.
- **`AnthropicCallError`** — single exception type for
  SDK failures. Callers that previously caught
  `RuntimeError` from `generate_docs()` should catch
  this (or its base `RuntimeError`) instead. The
  `[ai]` extra install hint is still surfaced on the
  missing-key path.
- **Typed Anthropic client** — `doc_gen/stages.py`
  functions now take `client: Anthropic` instead of
  `client: object`, restoring IDE autocomplete and
  catching SDK drift at check time.
- **Content-budget constants** — `OUTLINE_SOURCE_CHARS`,
  `WRITE_SOURCE_CHARS`, and `REVIEW_SOURCE_CHARS`
  replace the 4000/5000/3000 magic numbers previously
  inlined in `stages.py`.
- **MCP path validation helper** —
  `AttuneAuthorHandlers._validated_paths()` + a new
  internal `_PathValidationError` exception consolidate
  the four duplicated validate-and-return-error-dict
  blocks that appeared in `author_status`,
  `author_generate`, `author_maintain`, and
  `author_lookup`.
- **CLI split** — `cli.main()` is now a thin wrapper
  around `_build_parser()` and `_dispatch()`. The
  dispatch table is a mapping rather than an `if`
  ladder, which unlocks per-subcommand unit tests.
- **Autouse test fixture** — a new `conftest.py`
  fixture disables strict polish and strips
  `ANTHROPIC_API_KEY` for every test, so the suite
  stays offline without per-test mocking. Tests that
  specifically exercise strict-mode behavior override
  it with their own `patch.dict` blocks.
- **New tests** — strict-default `polish_template` test,
  API-key-redaction test for `call_anthropic`,
  symlink-chain traversal test for
  `validate_file_path`, preamble edge-case tests
  (frontmatter-only body, heading-only body, non-UTF-8
  file), and a zero-match-glob test for
  `generate_feature_templates`.

### Fixed (0.3.0)

- **Non-UTF-8 task templates crashed `get_preamble`.**
  The function's `read_text(encoding="utf-8")` call
  was wrapped in an `except OSError`, but
  `UnicodeDecodeError` inherits from `ValueError` and
  fell through to callers as an unhandled exception.
  Now caught alongside `OSError` and logged at debug
  level; the function returns `None` as documented.
  Discovered via the new preamble edge-case test.

### Internal (0.3.0)

- **Plugin-layout tests now skip when `plugin/` is
  absent.** `test_plugin_config.py` and
  `test_plugin_references.py` validate a Claude Code
  plugin layout that this source-only repo never
  scaffolded, and were surfacing as 9 failures + 18
  errors on every run. A module-level
  `pytestmark = pytest.mark.skipif(...)` hides them
  when the layout is missing and auto-enables them if
  it's ever built.

## [0.2.0] - 2026-04-11

### Added (0.2.0)

- **Tier-1 problem-shaped meta-templates** — four new
  template kinds that document failure modes rather than
  the happy path: `error.md.j2`, `warning.md.j2`,
  `troubleshooting.md.j2`, and `faq.md.j2`. Closes the
  largest part of the coverage gap with attune-help's
  consumer corpus (408 of the 633 stored templates in
  attune-help are in these four categories).
- **Tier-2 guidance-shaped meta-templates** — four
  additional kinds for opinionated and contextual
  content: `quickstart.md.j2`, `tip.md.j2`, `note.md.j2`,
  and `comparison.md.j2`. The generator now produces all
  11 template types that attune-help renders.
- **Per-type LLM polish prompts** — new
  `attune_author.polish_prompts` module with
  kind-specific system prompts for each of the 11
  template types. Each prompt teaches the LLM what
  "good" looks like for its kind (concepts want
  definitional clarity, tasks want "Use ... when"
  openers, troubleshooting wants symptom-table
  specificity, comparisons want decision rules, etc.).
- **Anti-pattern lists** — verbatim phrases from the
  auto-generated Jinja drafts that the polish pass asks
  the LLM to rewrite. More token-efficient than
  full few-shot examples.
- **Strict polish mode** — new `strict=` kwarg on
  `polish_template()` plus a `ATTUNE_AUTHOR_STRICT_POLISH`
  environment variable that makes polish failures hard
  errors instead of silent fallbacks. New `PolishError`
  exception type for clean catch sites.
- **Signature-aware source summaries** — `build_source_summary()`
  now accepts optional `function_signatures` and
  `class_signatures` kwargs that surface typed signatures
  (`name(arg: T = default) -> R`) instead of bare names.
  The generator extracts these via three new helpers:
  `_format_function_signature`, `_format_class_methods`,
  and `_unparse_annotation`.
- **Shared Jinja macros** — `meta_templates/_partials/problem_macros.j2`
  holds `related_functions`, `related_classes`,
  `key_files`, `tags_line`, and `feature_intro` macros
  used by all 8 new templates. No copy-paste, no template
  inheritance — just imported macros.
- **Dogfood help corpus** — `.help/features.yaml` and
  `.help/templates/<feature>/<kind>.md` document
  attune-author itself using its own pipeline. 9 features
  × 11 template kinds = 99 polished, source-grounded
  templates committed to the repo.
- **`scripts/regenerate_help.py`** — entry point for
  regenerating the dogfood corpus. Supports `--features`
  for targeting a subset and `--no-polish` for skipping
  the LLM call.

### Changed (0.2.0)

- `generate_feature_templates` now accepts the eight new
  template kinds via the `depths=` kwarg. Default
  behavior is unchanged — a call without `depths=` still
  produces only `concept`, `task`, and `reference`.
- Generated frontmatter now writes both the canonical
  `type:` field (what attune-help reads) and the legacy
  `depth:` field (kept for backward compatibility with
  any existing readers).
- `polish.py` routes to per-type system prompts based on
  the new `template_type` parameter on `polish_template()`.
- `polish_template()` now feeds LLM responses through a
  new `_sanitize_output()` helper that strips per-line
  trailing whitespace and ensures exactly one trailing
  newline. Fixes two real LLM output bugs caught during
  the dogfood run (the Anthropic API does not always
  emit a trailing newline, and the model occasionally
  produces `  ` markdown line breaks in tables).

### Tests (0.2.0)

- 173 new tests across the four PRs:
  - `test_problem_templates.py` — 34 tests for the
    tier-1 templates and the new template-kind constants.
  - `test_polish_improvements.py` — 58 tests for per-type
    prompts, strict mode, signature-aware summaries,
    AST signature extraction, and `_sanitize_output()`.
  - `test_guidance_templates.py` — 45 tests for the
    tier-2 templates and per-kind polish prompts.
  - `test_dogfood_help.py` — 17 structure tests that
    keep the `.help/` corpus well-formed forever.
- Three pre-existing tests in `test_polish.py` updated
  to match the new API (em-dash separator in the
  source summary, `template_type` parameter on
  `_call_llm`, sanitized return value).
- Full suite: 294 passed (up from 140 baseline). The
  9 pre-existing `test_plugin_*.py` failures are stale
  artifacts from the monorepo extraction and remain
  outside the scope of this release.

## [0.1.0] - 2026-04-09

### Added (0.1.0)

- Initial release. Standalone package extracted from the
  attune-ai monorepo. Includes the generator, polish,
  manifest, bootstrap, staleness, maintenance, preamble,
  CLI, MCP server, and 3-stage doc-gen pipeline modules.
