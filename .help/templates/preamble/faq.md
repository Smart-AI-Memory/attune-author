---
type: faq
feature: preamble
depth: faq
generated_at: 2026-04-14T16:13:18.376117+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble FAQ

## What is preamble?

Preamble provides context-sensitive one-liners that help workflow skills understand your current project state and recent activity.

## When should I use it?

Use preamble when you need contextual information for workflow skills. It automatically tailors help content based on what you're working on.

## What's the main entry point?

Start with `get_preamble()` to retrieve a one-liner for a specific feature. If you need related context, use `get_related_preambles()` to find similar features by shared tags.

Both functions are in `src/attune_author/preamble.py` and include detailed docstrings about inputs and outputs.

## How do I debug it?

Run `pytest -k "preamble" -v` first to check if the basic functionality works. If tests pass but your code fails, add `logger.debug` statements where you suspect issues and re-run with logging enabled.

For common problems, check the troubleshooting page for this feature.

## Where are the source files?

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
