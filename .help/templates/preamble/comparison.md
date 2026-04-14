---
type: comparison
feature: preamble
depth: comparison
generated_at: 2026-04-14T14:08:46.849600+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Comparison: Preamble vs alternatives

## Context

The preamble feature generates context-sensitive one-liner descriptions for workflow skills. It analyzes project state and recent activity to provide relevant contextual information that helps users understand what each skill does in their current situation.

## When to use preamble

Use preamble when you need dynamic, contextual descriptions for workflow features that adapt to the user's current project state. This feature excels at providing just-in-time information that's more relevant than static documentation.

Key capabilities that make preamble the right choice:

- `get_preamble()` — Retrieves a single contextual one-liner for a specific feature
- `get_related_preambles()` — Finds up to 3 related features based on shared tags, useful for discovery

## When NOT to use preamble

Preamble has specific limitations that make it unsuitable for certain use cases:

- **Static documentation needs** — If you need comprehensive, unchanging feature descriptions, use dedicated help files instead
- **Bulk operations** — The API is designed for individual feature lookups, not batch processing of many features at once
- **Complex contextual logic** — If you need sophisticated context analysis beyond project state and tags, you'll need a custom solution
- **Non-workflow features** — Preamble is specifically designed for workflow skills, not general project components

## Feature comparison

| Aspect | Preamble | Static help files | Custom context logic |
|--------|----------|------------------|---------------------|
| **Context awareness** | Dynamic based on project state | Fixed content | Fully customizable |
| **Performance** | Fast single lookups | Instant | Depends on implementation |
| **Maintenance** | Automatic updates | Manual editing required | Custom maintenance burden |
| **Scope** | Workflow skills only | Any documentation | Unlimited |
| **Discovery** | Built-in related features | Manual cross-references | Custom relationship logic |

## Use preamble when...

You need contextual, adaptive descriptions for workflow skills that help users understand what's relevant to their current project situation. Preamble is particularly valuable in interactive environments where users need quick, relevant information without diving into full documentation.

Choose alternatives when you need static comprehensive documentation, bulk processing capabilities, or context logic that goes beyond the built-in project state analysis.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
