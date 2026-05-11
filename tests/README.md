# attune-author tests

attune-author is the **reference layer for LLM mocking** in the attune
product family. The patterns documented below are what attune-rag,
attune-gui, and attune-help's `tests/README.md` files point at.

## Running locally

```bash
# Install dev deps (includes pytest-cov + syrupy)
pip install -e ".[dev]"

# Full suite (~76s — slowest of the four layers)
pytest

# With coverage (matches CI's ubuntu x py3.11 cell)
pytest --cov --cov-report=term-missing

# Update golden snapshots after a deliberate template change
pytest tests/test_generated_templates_golden.py --snapshot-update

# Opt in to live API tests (require ANTHROPIC_API_KEY)
pytest -m live
```

## LLM mocking standard

Three autouse fixtures in `conftest.py` form the reference pattern:

1. `_lenient_polish_by_default` — sets
   `ATTUNE_AUTHOR_STRICT_POLISH=false` and strips `ANTHROPIC_API_KEY`
   so a misconfigured test never reaches the network.
2. `_reset_rag_pipeline` — clears the module-level RagPipeline singleton
   between tests, so a leaked patch from one test doesn't poison
   subsequent tests.
3. Per-test patches use `unittest.mock.patch("anthropic.Anthropic")` at
   the **import boundary**, never at the call site.

The `live` marker gates real-API tests (`pytest -m live`), so they
never run by default.

## Test layout

| File | Purpose |
|------|---------|
| `test_generator.py` | `generate_feature_templates` happy paths, depth selection, frontmatter contract |
| `test_generated_templates_golden.py` | **NEW** syrupy snapshots of rendered concept/task/reference output (deterministic via timestamp + hash stripping) |
| `test_mcp_handlers_integration.py` | **NEW** AttuneAuthorHandlers full request → orchestration → response lifecycle |
| `test_parallel_polish_errors.py` | **NEW** `_parallel_polish` error injection (PolishError, TimeoutError, all-fail cascade) |
| `test_polish_*.py` | polish.py system-prompt selection, retry logic, source-summary assembly |
| `test_staleness*.py` | hash + frontmatter footer parsing; semantic-hash regen detection |
| `test_rag_hook.py` | `ground_polish_context` — singleton lifecycle, lazy import path |

## Snapshot policy

`test_generated_templates_golden.py` uses **syrupy** to pin generated
template output. Snapshots live in `tests/__snapshots__/`. To update
after a deliberate template change:

```bash
pytest tests/test_generated_templates_golden.py --snapshot-update
```

Snapshot diffs surface in PR review like a normal text file. The
helper `_stable()` strips timestamps and `source_hash` values before
comparison so reruns stay deterministic without `--snapshot-update`.

## What's tested vs. not

After pass 1, the highest-value remaining gaps are:

- `mcp/server.py` (~67%) — server lifecycle paths
- `cli.py` (~80%) — CLI error paths and help output
- Native-citations end-to-end (still gated on the weekly
  `rag-gate.yml`, which spends real Anthropic credits — pass 2 will
  audit + tighten that gate).

Pass 2 will revisit thresholds and target areas above.
