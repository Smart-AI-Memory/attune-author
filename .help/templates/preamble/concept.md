---
type: concept
feature: preamble
depth: concept
generated_at: 2026-04-11T04:55:18.812711+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Preamble

Preambles are one-line summaries that provide context-aware introductions to workflow skills based on your project state and recent activity.

## How preambles work

When you invoke a workflow skill, the system can display a brief, contextual summary at the beginning of the interaction. These preambles help orient you to what the skill does and why it might be relevant in your current situation.

The preamble system draws from two sources:

- **Individual feature preambles** — Each workflow skill can have its own one-liner that explains its purpose
- **Related feature suggestions** — The system can surface preambles for similar skills by analyzing shared tags between features

## Core functions

The preamble module exposes two functions for retrieving contextual information:

| Function | Purpose |
|----------|---------|
| `get_preamble()` | Retrieves the one-liner summary for a specific feature |
| `get_related_preambles()` | Finds up to 3 related features based on shared tags and returns their preambles |

Both functions accept a `help_dir` parameter to specify where feature documentation is stored, making the system adaptable to different project structures.

## Integration with workflow context

Preambles connect to the broader workflow system through three key areas: context awareness (adapting to your current project state), rendering (displaying information at appropriate moments), and workflow coordination (helping you discover related capabilities).
