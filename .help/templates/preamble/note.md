---
type: note
feature: preamble
depth: note
generated_at: 2026-04-11T04:56:34.471905+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Note: preamble

## Context

The preamble module provides context-sensitive one-liner descriptions for workflow skills. These preambles adapt based on your project state and recent activity to give you relevant context for each feature.

## Content

The preamble module exposes two main functions:

- `get_preamble()` — Returns a single one-liner description for a specified feature
- `get_related_preambles()` — Finds up to three features with related functionality based on shared tags and returns their preambles

Both functions accept an optional `help_dir` parameter to specify where to look for feature metadata, and they return `None` or empty results when no matching preambles exist.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
