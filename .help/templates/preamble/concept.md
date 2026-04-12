---
type: concept
feature: preamble
depth: concept
generated_at: 2026-04-12T04:19:48.399274+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble

A preamble is a one-line description that appears at the start of workflow skills to provide context about what the skill does and when to use it.

## How preambles work

The preamble system generates context-sensitive descriptions by matching feature names to stored one-liners. When you request a preamble for a specific feature, the system looks up the corresponding description and returns it as a string.

For example, if you request a preamble for a "code review" feature, you might get back "Analyze code changes for quality, security, and maintainability issues."

## Related feature discovery

Beyond individual preambles, the system can find features that share common tags or purposes. When you call `get_related_preambles()`, it returns up to three related features along with their preambles. This helps users discover workflow skills that work well together.

## Core functions

- **`get_preamble()`** — Retrieves the one-line description for a specific feature
- **`get_related_preambles()`** — Finds up to three related features and their descriptions based on shared tags

Both functions accept an optional `help_dir` parameter to specify where preamble data is stored, defaulting to the standard help directory location.
