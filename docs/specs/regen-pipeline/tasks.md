# Spec: Regen Pipeline — Tasks

## Phase 3: Tasks

**Status**: NOT done as written — reconciled 2026-06-06

> ## ⚠️ The task table below is INACCURATE
>
> A 2026-06-06 code audit found that **none** of the attune-author symbols in
> tasks 2–9 ever shipped (`_resolve_corpus_root`, `atomic_write`,
> `_patch_summaries_json`, `regen_template(corpus_root=…)`, `_regen`) and
> **none** of the attune-gui pieces in tasks 10–24 exist (`config.py`
> `ConfigState`, `/api/config`, `/api/templates/refresh-all`,
> `/api/browse/directory`, `CorpusSetup`, `App.jsx`). The "done" marks below are
> false. The earlier "Shipped" note conflated this spec with the unrelated
> hash-mismatch `attune-author regenerate` CLI — a different feature.
>
> **What actually satisfies the spec's user stories** (see `requirements.md`
> banner for the full mapping):
> - Single-doc regen → `POST /api/living-docs/docs/{id}/regenerate` (Jobs +
>   `attune_author.generator.generate_feature_templates`).
> - Corpus config → corpus registry (`editor_corpora.py`,
>   `/api/corpus/register`) + workspace config (`attune_gui.workspace`).
> - Bulk → `make regen-all` (Makefile).
>
> No code action is required: the product need is met. The table below is left
> intact only as a record of the original (unbuilt) plan.

### Implementation order

| # | Task | Layer | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Add `python-dotenv` to attune-author deps | attune-author | done | `pyproject.toml` required + ai extras |
| 2 | Add `_resolve_corpus_root(corpus_root)` helper | attune-author | done | param → `ATTUNE_CORPUS_ROOT` env → `.env` file → `RuntimeError` |
| 3 | Add `atomic_write(path, text)` helper | attune-author | done | Write to `path.with_suffix(".tmp")`, then `os.replace()` |
| 4 | Add `_patch_summaries_json(corpus_root, template_path, summary)` helper | attune-author | done | Load, update key, write back; no-op if file absent |
| 5 | Update `regen_template` signature to `(template_path, corpus_root=None)` | attune-author | done | Call `_resolve_corpus_root`; pass root to `_regen` |
| 6 | Implement `_regen(template_path, corpus_root)` | attune-author | done | Load .env, check API key, load template, Sonnet polish, Haiku summary, atomic write, patch summaries.json |
| 7 | Update `test_regen.py` for new signature | attune-author | done | Fix `assert_called_once_with` args |
| 8 | Add tests for `_resolve_corpus_root` | attune-author | done | param wins; falls back to env var; falls back to .env; raises when all missing |
| 9 | Add tests for `_regen` | attune-author | done | Mock `anthropic.Anthropic`; verify atomic write creates correct file; verify summaries.json patched; verify no-op when summaries.json absent |
| 10 | Add `attune_gui/config.py` — `ConfigState` singleton + `get_config()` / `set_corpus_root()` | attune-gui | done | Module-level `_config: ConfigState`; `set_corpus_root` calls `load_corpus` and stores root |
| 11 | Refactor `corpus_adapter.py` to use `config.get_config().corpus_root` | attune-gui | done | Remove module-level `_corpus`; delegate root tracking to config module |
| 12 | Add `attune_gui/routes/config.py` — `GET /api/config` and `POST /api/config` | attune-gui | done | POST validates path exists + is dir (422 otherwise); calls `set_corpus_root`; returns count |
| 13 | Add `GET /api/browse/directory` to config routes | attune-gui | done | osascript subprocess (replaced tkinter — crashes on macOS from non-main thread) |
| 14 | Wire config router into `main.py`; auto-load `ATTUNE_CORPUS_ROOT` on startup | attune-gui | done | Call `set_corpus_root` in FastAPI `lifespan` if env var is set |
| 15 | Update `_run_regen` in `ws.py` to pass `corpus_root` from config | attune-gui | done | `from attune_gui.config import get_config; root = get_config().corpus_root` |
| 16 | Add `POST /api/templates/refresh-all` to templates routes | attune-gui | done | Create jobs for all entries whose staleness is stale or warning; return 202 + job list |
| 17 | Add tests for `GET /api/config` and `POST /api/config` | attune-gui | done | GET returns null when unset; POST valid path returns count; POST missing path returns 422 |
| 18 | Add test for `GET /api/browse/directory` | attune-gui | done | Mocks osascript subprocess; asserts 200 with path and 204 on cancel |
| 19 | Add test for `POST /api/templates/refresh-all` | attune-gui | done | Mock `get_entries` with mixed staleness; assert only stale + warning get jobs; 202 response shape |
| 20 | Build `CorpusSetup` React component | attune-gui UI | done | Props: `onLoaded(corpusRoot)`; text input + Browse button + Load button; inline error on 422 |
| 21 | Update `App.jsx` — check `GET /api/config` on mount; show `CorpusSetup` when `corpus_root` is null | attune-gui UI | done | Replace template-list render with `<CorpusSetup>` until corpus is set |
| 22 | Update `DashboardSummaryBar` — add "Regen all stale" button | attune-gui UI | done | Shown when `stale + warning > 0`; fires `POST /api/templates/refresh-all`; shows running count |
| 23 | Update `App.jsx` — handle bulk regen response (connect WS per job, update badge per `done`/`error`) | attune-gui UI | done | Reuse `handleDone` / `handleError`; track count of completed jobs in summary bar button |
| 24 | Manual smoke test | attune-gui UI | done | Corpus loaded, stale badge clicked → spinner → fresh, "Regen all stale" confirmed working end-to-end |

### Testing strategy

- **attune-author (tasks 7–9)**: pytest unit tests. Mock `anthropic.Anthropic` to avoid real API calls. Use `tmp_path` for file I/O assertions.
- **attune-gui sidecar (tasks 17–19)**: pytest + FastAPI `TestClient`. Mock `tkinter.filedialog`, mock `get_entries`, mock `set_corpus_root` where needed.
- **attune-gui UI (tasks 20–23)**: No automated test suite yet. Task 24 (manual smoke) is the v1 acceptance gate.

### Rollback plan

- **attune-author (tasks 1–9)**: New helpers + signature change with default param — fully backwards compatible. Revert commits.
- **attune-gui sidecar (tasks 10–19)**: `config.py` is new; routes are additive; `_run_regen` change is small. Reverting does not break the existing staleness-badge feature.
- **attune-gui UI (tasks 20–23)**: `CorpusSetup` is a new component; `App.jsx` falls back gracefully if `GET /api/config` 404s. Revert commits.
