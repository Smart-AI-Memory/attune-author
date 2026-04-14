---
type: faq
feature: preamble
depth: faq
generated_at: 2026-04-14T14:08:20.990234+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble FAQ

## What is preamble?

Preamble provides context-sensitive one-liners for workflow skills based on your project's current state and recent activity.

## When should I use preamble?

Use preamble when you need to generate brief, contextual descriptions for features in your workflow. It's particularly useful for creating dynamic help text or summaries that adapt to what you're currently working on.

## How do I get a preamble for a specific feature?

Call `get_preamble()` with the feature name. It returns a one-line description or `None` if no preamble exists for that feature.

## How do I find related features?

Use `get_related_preambles()` to get preambles for features that share tags with your current feature. By default, it returns up to 3 related features.

## How do I debug preamble issues?

Run `pytest -k "preamble" -v` first to check if the tests pass. If your code still fails, add a `logger.debug` statement where you suspect the issue is and re-run with logging enabled.

## Where are the source files?

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
