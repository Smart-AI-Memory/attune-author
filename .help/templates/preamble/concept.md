---
type: concept
feature: preamble
depth: concept
generated_at: 2026-04-14T16:12:19.278638+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble

Preamble provides context-sensitive one-line descriptions for workflow skills, helping users understand what each feature does and discover related capabilities.

## Core functionality

The preamble system retrieves brief explanations for features and suggests related tools based on shared characteristics. When you request information about a specific feature, preamble returns a concise description that explains the feature's purpose within your current workflow context.

The system also connects features through shared tags, allowing you to discover related capabilities. For example, if you're working with a documentation feature, preamble can suggest other documentation-related tools that might be relevant to your current task.

## Key operations

- **`get_preamble()`** — Retrieves the one-line description for a specific feature
- **`get_related_preambles()`** — Finds up to three related features based on shared tags and returns their descriptions

## Integration points

Other parts of the codebase access preamble functionality through these functions:

| Function | Purpose | File |
|----------|---------|------|
| `get_preamble()` | Retrieves the one-line description for a specific feature | `src/attune_author/preamble.py` |
| `get_related_preambles()` | Finds up to three related features based on shared tags and returns their descriptions | `src/attune_author/preamble.py` |
