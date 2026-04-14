# Changelog

All notable changes to attune-author are documented in this
file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
