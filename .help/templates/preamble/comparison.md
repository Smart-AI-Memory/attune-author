---
type: comparison
feature: preamble
depth: comparison
generated_at: 2026-04-14T16:13:42.959709+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Comparison: Preamble vs alternatives

## Context

The preamble feature provides context-aware one-line summaries for workflow skills. It renders these summaries based on your project's current state and recent activity, helping you quickly understand what each feature does in your specific context.

## When to use preamble

Use preamble when you need contextual feature descriptions that adapt to your workflow state. This feature excels at providing relevant, timely information about available tools.

Key functions that make preamble the right choice:

- `get_preamble()` — Returns a single contextual summary for any feature name
- `get_related_preambles()` — Finds up to 3 related features based on shared tags

Choose preamble for interactive help systems, documentation that adapts to project context, or any interface where you need brief but relevant feature descriptions.

## When NOT to use preamble

Preamble has specific limitations that make it unsuitable for certain tasks:

- **Static documentation**: Preamble generates dynamic content based on context, so it's not suitable for fixed help text or documentation that needs to remain constant
- **Detailed explanations**: The feature provides one-line summaries only — use dedicated documentation features for comprehensive guides or tutorials
- **Non-feature content**: Preamble works with workflow skills and features, not arbitrary content or custom help topics
- **Bulk operations**: The API handles individual feature lookups efficiently but isn't optimized for generating hundreds of preambles at once

## Comparison with related features

| Feature | Purpose | Output Format | Context Awareness |
|---------|---------|---------------|-------------------|
| **Preamble** | Quick feature summaries | One-line strings | Full context integration |
| Documentation generators | Comprehensive guides | Multi-page content | Static or minimal context |
| Help systems | Interactive assistance | Structured responses | User session context |

Preamble is faster for quick lookups but less comprehensive than full documentation features. It provides more context than static help but less interactivity than full help systems.

## Use preamble when...

- You need brief, contextual descriptions of workflow features
- Your interface shows multiple feature options and needs relevant summaries
- You want help text that adapts to the current project state
- You're building discovery interfaces where users browse related features

Choose alternatives when you need detailed documentation, static help content, or explanations that go beyond single-line summaries.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
