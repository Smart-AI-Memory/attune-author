# Changelog

All notable changes to attune-author are documented in this
file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
