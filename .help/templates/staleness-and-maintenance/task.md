---
feature: staleness-and-maintenance
depth: task
generated_at: 2026-06-06T23:19:48.577723+00:00
source_hash: a32e9d9904602f0f282f0bf02f119e350efd6c8b4ecb73c04564917b6ae65f69
status: generated
---

# Work with staleness and maintenance

Use staleness and maintenance when you need to detect when generated templates are out of date with their source files and regenerate stale ones
.

## Prerequisites

- Access to the project source code
- Familiarity with the files under src/attune_author/staleness.py

## Steps

1. **Understand the current behavior.**
   Read the entry points to see what staleness and maintenance
   does today before making changes.
   The primary functions are:
   - `compute_semantic_hash()` in `src/attune_author/staleness.py` — Compute a semantic SHA-256 hash of a feature's Python source files.
   - `compute_source_hash()` in `src/attune_author/staleness.py` — Compute SHA-256 hash of a feature's source files.
   - `parse_doc_footer()` in `src/attune_author/staleness.py` — Parse an attune-generated HTML comment footer.
   - `build_doc_footer()` in `src/attune_author/staleness.py` — Build an attune-generated HTML comment footer line.
   - `check_staleness()` in `src/attune_author/staleness.py` — Check staleness across help templates and project docs.
2. **Locate the right function to change.**
   Each function has a single responsibility. Read its
   docstring, parameters, and return type to confirm it
   owns the behavior you need to modify.

3. **Make your change.**
   Follow existing patterns in the file — naming
   conventions, error handling style, and logging.

4. **Run the related tests.**
   This catches regressions before they reach other
   developers. Target with `pytest -k "staleness-and-maintenance"`.

## Key files

- `src/attune_author/staleness.py`
- `src/attune_author/maintenance.py`

## Common modifications

Functions you are most likely to modify:

- `compute_semantic_hash()` in `src/attune_author/staleness.py`
- `compute_source_hash()` in `src/attune_author/staleness.py`
- `parse_doc_footer()` in `src/attune_author/staleness.py`
- `build_doc_footer()` in `src/attune_author/staleness.py`
- `check_staleness()` in `src/attune_author/staleness.py`
- `check_workspace_staleness()` in `src/attune_author/staleness.py`
- `run_maintenance()` in `src/attune_author/maintenance.py`
- `get_changed_files()` in `src/attune_author/maintenance.py`
