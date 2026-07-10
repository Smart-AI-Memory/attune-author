---
type: concept
name: rag-hook-concept
feature: rag-hook
depth: concept
generated_at: 2026-07-10T13:12:16.847805+00:00
source_hash: 19b577bbd2525cae2917679bdac6c3c7051a2eb5ba988b8fc0be275b7c6eef09
status: generated
scaffold_hash: e451bbc3a9e666fbc1d0670ba83dec90f6410a25eda9bccac2432d673f6a6f6a
---

# RAG hook

The RAG hook is an optional grounding step in the attune-author polish pass: before the LLM rewrites a template, the hook retrieves related attune-help templates through attune-rag and injects them as context, so the rewrite references real, existing patterns instead of inventing them.

## How it works

The hook lives in `attune_author.rag_hook` and exposes two functions:

- **`rag_enabled() -> bool`** — Returns `True` when RAG grounding should be used. The polish pass calls this first as a cheap gate before doing any retrieval work. You can disable grounding by setting the `ATTUNE_AUTHOR_RAG` environment variable.
- **`ground_polish_context(feature_name: str, template_type: str, k: int = 3) -> str | None`** — Builds the grounding context block for the polish pass. Given a feature name and template type, it retrieves up to `k` related templates (three by default) and returns them as a formatted context string. It returns `None` when nothing useful is available, so callers can skip grounding cleanly.

The module uses lazy imports and degrades gracefully: if the `[rag]` extra isn't installed, attune-author still works — the polish pass simply runs without grounding. This keeps the base package installable without pulling in retrieval dependencies.

A useful mental model: the hook is a fetch-and-format layer between the polish pass and attune-rag. The polish pass asks "is grounding on?" (`rag_enabled()`), then "what should the LLM see?" (`ground_polish_context()`), and the hook handles retrieval, formatting, and every failure mode in between.

## Connection points

The hook sits at the boundary between attune-author's polish pass and the attune-rag retrieval layer. Related concerns: retrieval, grounding, the polish pass, and optional-extra packaging.

Other parts of the codebase call into the hook through these functions:

| Function | Purpose | File |
|----------|---------|------|
| `rag_enabled()` | Return `True` when RAG grounding should be used. | `src/attune_author/rag_hook.py` |
| `ground_polish_context()` | Build a grounding context block for the polish pass. | `src/attune_author/rag_hook.py` |
