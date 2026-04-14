---
type: concept
feature: preamble
depth: concept
generated_at: 2026-04-14T14:07:21.835547+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble

Preambles are one-line descriptions that provide context-sensitive summaries of workflow skills based on your project's current state and recent activity.

## Core functionality

When you're working with workflow skills, preambles help you quickly understand what each feature does and find related capabilities. The system delivers these brief explanations through two key operations:

- **Feature lookup** — `get_preamble()` retrieves the contextual description for any specific feature
- **Related feature discovery** — `get_related_preambles()` finds up to three features with shared tags, helping you explore connected functionality

## Integration points

Other parts of the system access preamble functionality through these entry points:

| Function | Purpose | File |
|----------|---------|------|
| `get_preamble()` | Get the one-liner preamble for a feature. | `src/attune_author/preamble.py` |
| `get_related_preambles()` | Get preambles for features related by shared tags. | `src/attune_author/preamble.py` |

The preamble system connects to context analysis, content rendering, and workflow management components to deliver relevant, timely descriptions.
