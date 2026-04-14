---
type: note
feature: preamble
depth: note
generated_at: 2026-04-14T16:13:37.847561+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Note: preamble

## Context

The preamble module provides context-sensitive one-liner descriptions for workflow skills. These preambles help users understand what a feature does based on current project state and recent activity.

## Functions

The module exposes two main functions:

- `get_preamble(feature_name, help_dir)` — Returns a one-liner description for a specific feature
- `get_related_preambles(feature_name, help_dir, max_results)` — Returns preambles for up to 3 features that share tags with the specified feature

Both functions are designed to be called directly without instantiating a class. The `help_dir` parameter is optional and defaults to the standard help directory location.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
