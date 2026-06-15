# Findings — doc-automation-consolidation

**Status:** Draft (2026-06-14)
**Owner:** Patrick
**How gathered:** read-only sweep of attune-ai (`/Users/patrickroebuck/attune-ai`)
and attune-author (this repo), 2026-06-14, while investigating why
attune-author polishes docs without an API key but attune-ai appears
to require one.

These are the load-bearing facts the design rests on. Verify before
acting — point-in-time observations.

---

## F1 — The polish logic is forked AND diverged, not shared

attune-ai carries its own copy of the help-polish LLM call:

- `attune-ai/src/attune/help/polish.py:95-97` — `_call_llm()` raises
  `RuntimeError("ANTHROPIC_API_KEY not set")` when the env var is
  missing. **Key-only. No subscription routing.**
- attune-author `src/attune_author/polish.py` (+ `auth.py`) — routes
  through `call_llm()` which prefers the Claude subscription under
  Claude Code (`CLAUDECODE=1` + `claude-agent-sdk`), no key required.

So it is not "one implementation used two ways" — it is **two
implementations that have drifted**: one keyless (author), one
key-only (ai). This is the root of the original confusion.

## F2 — attune-ai's in-process polish call has been broken since day one

`attune-ai/src/attune/memory/personal.py:335`:

```python
result = polish_fn(text, template_type=kind)
```

attune-author's `polish_template` signature (unchanged since the
initial commit `23522c4`, confirmed via `git log -L`):

```python
def polish_template(content, feature_name, source_summary,
                    template_type="generic", ...)
```

`feature_name` and `source_summary` are **required positionals with
no defaults**. The attune-ai call supplies neither, so it raises
`TypeError: missing 2 required positional arguments`. The call is
wrapped in `try/except Exception` (`personal.py:341`):

- non-strict (default): logs `personal_memory_polish_failed` and
  returns the **unpolished** skeleton — a silent no-op.
- strict: re-raises → crash.

Implication: the in-process memory-polish integration has never
actually polished anything. **A version bump does not fix this** —
the call site is wrong against every version.

## F3 — attune-ai key-demand sites (where a key is really needed)

| Site | Tag |
|---|---|
| `src/attune/llm/providers/anthropic.py:93` | HARD-REQUIRED (native provider ctor) |
| `src/attune/llm/providers/anthropic_batch.py:44` | BATCHES-ONLY (no subscription path exists) |
| `src/attune/help/polish.py:95` | HARD-REQUIRED (the forked help polish) |
| `agent_factory/adapters/langchain_adapter.py:248` | only if LangChain adapter used |
| `agent_factory/adapters/langgraph_adapter.py:253` | only if LangGraph adapter used |

attune-ai's **core workflows** (code-review, security, bug-predict,
test-gen) call `claude_agent_sdk.query()` via `sdk_isolation_kwargs()`
and are already keyless under Claude Code. The most likely thing the
user hit is the **help-polish path** (F1) — key-only by construction.

## F4 — The dependency cap is conservative policy, not a known break

`attune-ai/pyproject.toml` `[author]` extra:

```python
author = [
    "attune-author>=0.6.2,<0.16",
    "attune-help>=0.10.0",
]
```

- The `<0.16` cap follows the repo-wide policy of gating each minor
  bump on explicit re-validation (commit `b4c05fe14`, 2026-06-10
  admitted 0.15.0; the comment notes 170 rag/help tests green).
- It is **not** guarding a specific incompatibility.
- The `[author]` extra is documented "*NOT a runtime requirement*" —
  workspace/dev tooling.

## F5 — attune-ai's consumption surface of attune-author is small and stable

- **CLI (subprocess)** — `ops/help_regen.py`, `ops/help_data.py`:
  `attune-author generate <feature> [--all-kinds]`,
  `attune-author regenerate [--dry-run]`,
  `attune-author status`, all with `--project-root` / `--help-dir`.
  All present and unchanged in 0.17.
- **Python import** — only `attune_author.polish.polish_template`
  (the broken call, F2).
- **Load-bearing**: attune-ai parses `attune-author status` output as
  markdown (`tests/unit/ops/test_help_data.py` `_parse_status_output`
  / `_TABLE_ROW_RE`). A status-format change in author would break
  staleness detection — verify the format is unchanged before bumping.

## F6 — attune-help transitive coupling

attune-author 0.15.0 moved attune-help out of its core deps, so
attune-ai no longer receives it transitively; ai now pins
`attune-help>=0.10.0` directly in the `[author]` extra. Any change to
author's dep tiers must keep this in mind.

## F7 — Adjacent, already-identified work this overlaps

- **regen-pipeline reconciled** (project memory): the old regen
  pipeline was never built as designed; the need was met by
  "living-docs regen + corpus registry." A maintenance-mode registry
  is plausibly that registry gaining a column.
- **MCP tool namespace consolidation** (project memory): `help_*`
  (attune-ai) vs `lookup_*` (attune-help) vs `author_*`
  (attune-author) overlap; flagged as needing a dedicated plan, not a
  patch. This spec is adjacent — keep boundaries aligned.
