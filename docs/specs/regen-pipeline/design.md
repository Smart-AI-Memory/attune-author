# Spec: Regen Pipeline — Design

## Phase 2: Design

**Status**: in-review

---

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  attune-gui React UI                                             │
│  CorpusSetup  →  path input + Browse button + Load button        │
│  App          →  DashboardSummaryBar + "Regen all stale" button  │
│  StaleBadge   →  per-row refresh (unchanged)                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP / WebSocket
┌────────────────────────▼─────────────────────────────────────────┐
│  attune-gui FastAPI sidecar                                      │
│  GET  /api/config                 ← read current corpus root     │
│  POST /api/config                 ← set corpus root + reload     │
│  GET  /api/browse/directory       ← native dir picker (macOS)    │
│  POST /api/templates/refresh-all  ← bulk regen, returns job IDs  │
│  (existing endpoints unchanged)                                  │
└──────────┬──────────────────────────────┬────────────────────────┘
           │ library call                 │ library call
┌──────────▼───────────┐  ┌──────────────▼────────────────────────┐
│  attune-rag          │  │  attune-author                        │
│  DirectoryCorpus     │  │  regen_template(path, corpus_root)    │
│  (unchanged)         │  │  _regen → polish + summary + write    │
└──────────────────────┘  └───────────────────────────────────────┘
```

---

### API changes

#### New: `GET /api/config`

```
Response 200:
{
  "corpus_root": "/abs/path/to/templates" | null
}
```

Returns the currently loaded corpus root. `null` if no corpus is loaded.

---

#### New: `POST /api/config`

```
Request:  { "corpus_root": "/abs/path/to/templates" }
Response 200:
{
  "corpus_root": "/abs/path/to/templates",
  "template_count": 26
}
```

Validates the path exists, calls `load_corpus(corpus_root)`, returns the count.
Returns 422 if the path does not exist or is not a directory.

---

#### New: `GET /api/browse/directory`

Opens a native macOS Finder directory-picker dialog (via `tkinter.filedialog`) in a
thread, waits for the user to select a folder, and returns the chosen path.

```
Response 200: { "path": "/abs/path/to/templates" }
Response 204: {}   ← user cancelled the dialog
```

This endpoint blocks until the dialog closes (typically < 5s). The frontend fires it
on Browse button click and populates the path input with the result.

---

#### New: `POST /api/templates/refresh-all`

Creates refresh jobs for every template whose current staleness is `"stale"` or
`"warning"`. Returns all job IDs immediately (202); the client connects to each WS
individually using the existing `WS /ws/refresh/{job_id}` endpoint.

```
Response 202:
{
  "jobs": [
    { "job_id": "uuid", "path": "concepts/auth.md", "status": "pending" },
    ...
  ],
  "total": 8
}
```

---

### attune-author: `regen_template` signature change

```python
def regen_template(
    template_path: str,
    corpus_root: str | Path | None = None,
) -> None:
```

Resolution order for `corpus_root`:
1. Explicit parameter
2. `ATTUNE_CORPUS_ROOT` environment variable
3. `.env` file in the current working directory (`python-dotenv` loads it at call time)
4. `RuntimeError` — cannot proceed

`_regen` implementation flow:

```
1. _resolve_corpus_root(corpus_root)       → Path
2. load .env (python-dotenv) if present
3. check ANTHROPIC_API_KEY — raise RuntimeError if missing
4. full_path = corpus_root / template_path — raise FileNotFoundError if missing
5. post = frontmatter.load(full_path)
6. client = anthropic.Anthropic()
7. polish_response = client.messages.create(
       model="claude-sonnet-4-6",
       max_tokens=4096,
       system=[{"type":"text","text":SYSTEM_POLISH,"cache_control":{"type":"ephemeral"}}],
       messages=[{"role":"user","content": post.content}]
   )
8. improved = polish_response.content[0].text
9. summary_response = client.messages.create(
       model="claude-haiku-4-5-20251001",
       max_tokens=128,
       messages=[{"role":"user","content": f"One sentence summary:\n\n{improved}"}]
   )
10. post.content = improved
11. post.metadata["summary"] = summary_response.content[0].text.strip()
12. atomic_write(full_path, frontmatter.dumps(post))   ← temp → rename
13. _patch_summaries_json(corpus_root, template_path, post.metadata["summary"])
```

`atomic_write`: write to `full_path.with_suffix(".tmp")`, then `os.replace()`.
`_patch_summaries_json`: load `corpus_root/summaries.json` if present, update the
matching key, write back. No-op if file absent.

---

### Data model changes

**New: `ConfigState`** (in `attune_gui/config.py`, module-level singleton)

```python
class ConfigState(BaseModel):
    corpus_root: Path | None = None
```

Replaces the current implicit `_corpus` in `corpus_adapter.py`. Both modules share it.

**No changes** to `TemplateEntry`, `JobState`, or `summaries.json` schema.

---

### UI/UX

#### Corpus setup screen (shown when `corpus_root is None`)

```
┌──────────────────────────────────────────────────────────────┐
│  Attune Template Dashboard                                   │
│                                                              │
│  No corpus loaded.                                           │
│  ┌─────────────────────────────────────┐ [Browse] [Load]    │
│  │ /path/to/templates                  │                    │
│  └─────────────────────────────────────┘                    │
│  ← inline error if path invalid                             │
└──────────────────────────────────────────────────────────────┘
```

- **Browse** fires `GET /api/browse/directory`; populates the text input with returned path.
  Disabled + shows spinner while the dialog is open.
- **Load** fires `POST /api/config`; on success replaces the setup screen with the
  template list. On 422, shows the error message inline below the input.

#### "Regen all stale" button (shown when `summary.stale > 0 || summary.warning > 0`)

Placed in `DashboardSummaryBar`, after the counts:

```
● 3 stale  ·  ● 5 warning  ·  26 total    [Regen all stale]
```

Click flow:
1. Button fires `POST /api/templates/refresh-all`.
2. For each returned job, connects a WebSocket as normal.
3. Button shows "Regenerating 8…" with a running count of completed jobs.
4. Button re-enables when all jobs reach `done` or `error`.
5. Rows update badge-by-badge via existing `onDone` / `onError` logic.

---

### Cross-layer impact

| Order | Layer | Change |
|-------|-------|--------|
| 1 | attune-author | `regen_template` signature + `_regen` implementation; add `python-dotenv` dep |
| 2 | attune-gui sidecar | `config.py` module; 3 new routes; `_run_regen` passes corpus root; sidecar startup auto-loads from env |
| 3 | attune-gui UI | `CorpusSetup` component; `DashboardSummaryBar` gains Regen-all button; `App` checks corpus state on mount |

attune-rag and attune-help: no changes.

---

### Tradeoffs & alternatives

| Option | Pros | Cons | Chosen? |
|--------|------|------|---------|
| tkinter dir picker via sidecar endpoint | Native macOS dialog, no Electron | Blocks sidecar thread; must run in thread pool; won't work headless | **Yes** |
| Web File System Access API | Pure browser, no sidecar change | Returns `FileSystemDirectoryHandle`, not a path string — useless for sidecar | No |
| Startup flag only (`--corpus`) | Simplest | No in-app reconfiguration; fails the UX requirement | No |
| Bulk regen via individual POST per badge | Reuses existing flow | N clicks, no single "regen all" affordance | No |
| Bulk regen `refresh-all` endpoint | Single click, server manages job creation | Slightly more server code | **Yes** |
| python-dotenv for API key | Dev-friendly; key lives in `.env` alongside code | Adds a dep to attune-author | **Yes** |
