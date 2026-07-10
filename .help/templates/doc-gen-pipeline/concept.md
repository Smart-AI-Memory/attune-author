---
type: concept
name: doc-gen-pipeline-concept
feature: doc-gen-pipeline
depth: concept
generated_at: 2026-07-10T13:11:24.164288+00:00
source_hash: 133624bd892c65fc1107ef6e8ac7503496aa666e58699b21c2121e800ebee9bc
status: generated
scaffold_hash: 032fe8241bb372e34b06fdaa427e097d5a903d0720bb6c21fa7f0b2cd7b7cfd7
---

# Doc Gen Pipeline

The doc-gen pipeline generates documentation from source code in three LLM-driven stages — outline, write, review — so each stage can focus on one job instead of producing an entire document in a single pass.

## How it works

You call `generate_docs(target, config, output_path)` with a source file or content, and the pipeline runs three stages in order:

1. **Outline** — `build_outline()` reads the source content and produces a structured documentation outline for the given `doc_type` and `audience`.
2. **Write** — `write_content()` expands that outline into full documentation, drawing on the source content. You can narrow this stage to specific sections with `section_focus`.
3. **Review** — `review_content()` polishes the draft against the original source, catching inaccuracies and rough prose before you see the result.

Between stages, `parse_outline_sections()` extracts top-level section titles from the outline, which lets the write stage work through the document in chunks (`sections_per_chunk` in the config controls the chunk size).

Two dataclasses carry state through the pipeline:

- **`DocGenConfig`** — your inputs: what kind of doc to produce (`doc_type`, default `'api-reference'`), who it's for (`audience`, default `'developers'`), which model to use, and per-stage token budgets (`max_outline_tokens`, `max_write_tokens`, `max_review_tokens`).
- **`DocGenResult`** — the outputs: the final `content`, plus the intermediate `outline` and `draft`, a `stages_completed` list, and the `source_path` that was documented. Because the intermediates are preserved, you can inspect where in the pipeline a bad result originated.

The mental model: `generate_docs()` is the orchestrator, the three stage functions in `doc_gen.stages` do the work, and the config and result dataclasses are the contract on either side.

## What connects to it

The pipeline requires the Anthropic client — each stage function takes a `client: Anthropic` parameter. If the client isn't available, `generate_docs()` raises `AnthropicCallError` with instructions to install the `attune-author[ai]` extra.

Other parts of the codebase interact with the pipeline through these interfaces:

| Interface | Purpose | File |
|-----------|---------|------|
| `generate_docs()` | Entry point: run the full pipeline on a source file or content | `src/attune_author/doc_gen/pipeline.py` |
| `DocGenConfig` | Configuration for the document generation pipeline | `src/attune_author/doc_gen/config.py` |
| `DocGenResult` | Result of document generation, including intermediate stages | `src/attune_author/doc_gen/pipeline.py` |
