---
feature: polish
depth: task
generated_at: 2026-06-06T23:19:48.562428+00:00
source_hash: 79da77a01c4b4a11716e33f5673ee64882fe6354c51b6cf999aee80d9dbe4b7e
status: generated
---

# Work with polish

Use polish when you need to improve generated template quality with an llm rewrite pass that uses per-type system prompts and source-grounded summaries
.

## Prerequisites

- Access to the project source code
- Familiarity with the files under src/attune_author/polish.py

## Steps

1. **Understand the current behavior.**
   Read the entry points to see what polish
   does today before making changes.
   The primary functions are:
   - `clear_cache()` in `src/attune_author/polish.py` — Delete every entry in the polish cache directory.
   - `polish_template()` in `src/attune_author/polish.py` — Polish a generated template using an LLM.
   - `build_polish_prompt()` in `src/attune_author/polish.py` — Build the (system_prompt, user_message) pair for a polish call.
   - `reset_polish_cache_telemetry()` in `src/attune_author/polish.py` — Reset the per-process prompt-cache telemetry counters.
   - `polish_cache_stats()` in `src/attune_author/polish.py` — Snapshot the current per-process prompt-cache aggregate.
2. **Locate the right function to change.**
   Each function has a single responsibility. Read its
   docstring, parameters, and return type to confirm it
   owns the behavior you need to modify.

3. **Make your change.**
   Follow existing patterns in the file — naming
   conventions, error handling style, and logging.

4. **Run the related tests.**
   This catches regressions before they reach other
   developers. Target with `pytest -k "polish"`.

## Key files

- `src/attune_author/polish.py`
- `src/attune_author/polish_prompts.py`

## Common modifications

Functions you are most likely to modify:

- `clear_cache()` in `src/attune_author/polish.py`
- `polish_template()` in `src/attune_author/polish.py`
- `build_polish_prompt()` in `src/attune_author/polish.py`
- `reset_polish_cache_telemetry()` in `src/attune_author/polish.py`
- `polish_cache_stats()` in `src/attune_author/polish.py`
- `format_polish_cache_summary()` in `src/attune_author/polish.py`
- `build_source_summary()` in `src/attune_author/polish.py`
- `get_system_prompt()` in `src/attune_author/polish_prompts.py`
