# Changelog

All notable changes to attune-author are documented in this
file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
