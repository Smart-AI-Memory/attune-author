---
type: faq
feature: preamble
depth: faq
generated_at: 2026-04-11T04:56:15.887647+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Preamble FAQ

## What is preamble?

The preamble feature provides context-sensitive one-liner descriptions for workflow skills based on your current project state and recent activity.

## When should I use it?

Use preamble when you need to display brief, contextual descriptions of features or skills in your workflow interface. It's designed to help users understand what each feature does in relation to their current work.

## What's the main entry point?

Start with these two functions:

- `get_preamble()` — Returns a one-liner description for a specific feature
- `get_related_preambles()` — Returns preambles for features that share tags with your target feature

Both functions are in `src/attune_author/preamble.py`. Check their docstrings for input and output details.

## How do I debug it?

First, run the tests: `pytest -k "preamble" -v`. If tests pass but your code fails, add `logger.debug` statements at suspected failure points and re-run with logging enabled.

For common issues, check the troubleshooting page for this feature.

## Where are the source files?

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
