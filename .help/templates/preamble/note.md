---
type: note
feature: preamble
depth: note
generated_at: 2026-04-14T14:08:40.851736+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Note: preamble

## Context

The preamble module provides context-sensitive introductory text for workflow skills. It generates one-line descriptions that reflect the current project state and recent activity, helping users understand what each skill does in their specific situation.

## Implementation

The preamble module exposes two main functions:

- `get_preamble()` — Returns a contextual one-liner description for a specific feature
- `get_related_preambles()` — Finds up to 3 related features based on shared tags and returns their preambles

Both functions accept an optional `help_dir` parameter to specify where to look for feature metadata. The related preambles function uses tag overlap to identify conceptually similar features.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
