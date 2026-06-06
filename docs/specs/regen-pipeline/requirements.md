# Spec: Regen Pipeline

> Extends the staleness-badge feature. Completes task 18 (smoke test) by implementing
> `attune_author.regen._regen` and wiring corpus root through the sidecar + UI.

---

> ## ⚠️ RECONCILED — satisfied-by-different-means (2026-06-06)
>
> This spec was previously marked "complete" with all tasks ✅, but a code
> audit found **none** of its named symbols ever shipped (`_regen`,
> `regen_template(corpus_root=…)`, `_resolve_corpus_root`, `atomic_write`,
> `_patch_summaries_json`) and the attune-gui pieces (`/api/config`,
> `refresh-all`, `CorpusSetup`) do not exist. The underlying need was instead
> met by a **more evolved architecture**. All three user stories are satisfied:
>
> | User story | Status | Actual implementation |
> |---|---|---|
> | US1 — badge click → regen → saved to disk | ✅ met | `POST /api/living-docs/docs/{id}/regenerate` → Jobs registry → `_regenerate_doc_executor` → `attune_author.generator.generate_feature_templates` (`sidecar/attune_gui/routes/living_docs.py`). Source-driven generation, not polish+Haiku. |
> | US2 — first-run corpus setup UI | ✅ exceeded | Multi-corpus registry: `editor_corpora.py`, `POST /api/corpus/register`, `editor-frontend/src/corpus-switcher.ts` (dropdown + "Add corpus…" modal). |
> | US3 — env auto-load on startup | ✅ met | Workspace config (`living_docs.py` `get_config`/`set_config`, `attune_gui.workspace`) + persisted corpus registry, replacing single `ATTUNE_CORPUS_ROOT`. |
>
> Bulk regen ships as the build-time `make regen-all` target (Makefile), not a
> runtime "Regen all stale" button. The frontend is **TypeScript**, not the
> React/JSX assumed by `design.md`.
>
> **No genuine product gaps remain.** This spec is retained for history; the
> `design.md` below is **obsolete** (see its banner). Do not implement it.

## Phase 1: Requirements

**Status**: reconciled — satisfied by living-docs regen automation + corpus registry (was falsely marked "approved/complete")

### Problem statement

The staleness-badge feature (tasks 1–17) is complete. Task 18 requires `_regen` to
be callable end-to-end: clicking a stale badge in the dashboard must regenerate the
template file on disk and clear the badge to "fresh". Currently `_regen` raises
`NotImplementedError`, so the smoke test cannot run.

Additionally, the sidecar has no way to know where templates live on disk, and the
dashboard has no UI for pointing it to the right corpus root.

### Scope

**In scope:**

- Implement `attune_author.regen._regen(template_path, corpus_root)`:
  - Load the existing template file
  - Call Claude (Sonnet) to polish the Markdown content
  - Call Claude (Haiku) to generate a fresh one-sentence summary
  - Write the result back atomically (temp file → rename)
  - Update the `summary` field in the file's YAML frontmatter
  - Patch the matching entry in `summaries.json` (if present in corpus root)
- Add `corpus_root: str | Path | None = None` to `regen_template` public signature
  (env var `ATTUNE_CORPUS_ROOT` as fallback)
- Sidecar: auto-load corpus from `ATTUNE_CORPUS_ROOT` at startup; expose
  `GET /api/config` and `POST /api/config` to read/set the corpus root at runtime
- Sidecar WS handler: pass corpus root to `regen_template`
- Dashboard UI: if corpus root is not loaded on startup, show a text input + "Load"
  button at the top of the template list; once set, templates appear normally
- Native directory picker (Browse button — text input + "Load" )
- Bulk regen (regenning all stale templates at once)

**Out of scope:**

- Rollback history / undo
- Embedding freshness into a separate freshness-score field (staleness is mtime-based)
- Updating `summaries.json` entries for templates other than the one being regenned

### User stories

1. As a developer, I click a stale badge and the template is polished by Claude and
   saved to disk, so my corpus stays current without manual editing.
2. As a developer running the dashboard for the first time, I can type my corpus root
   path in a field and click "Load" so templates appear without needing to set an env var.
3. As a developer who sets `ATTUNE_CORPUS_ROOT` before starting the sidecar, templates
   load immediately on first open — no setup screen.

### Edge cases & open questions

| Question / Edge case | Resolution |
|---|---|
| Template file has no existing `summary` in frontmatter | Create the field; don't fail |
| `summaries.json` does not exist in corpus root | Skip the update; don't create the file |
| Claude API key is in the projects .env files | Fail with `RuntimeError("ANTHROPIC_API_KEY not set")`; sidecar emits error frame |
| Template file is missing from corpus root | Fail with `FileNotFoundError`; sidecar emits error frame |
| Polish call returns content that drops YAML-looking lines | Replace only `post.content`; frontmatter metadata is never touched by the LLM |
| User types a non-existent path in the corpus root field | Sidecar returns 422; UI shows inline error |
| Atomic write: process killed between temp write and rename | Temp file left behind (acceptable); original intact |

### Affected layers

- [x] attune-rag — no changes
- [x] attune-gui (sidecar + UI)
- [x] attune-author
- [ ] attune-help — no changes
