---
type: comparison
feature: preamble
depth: comparison
generated_at: 2026-04-11T04:56:39.197188+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Comparison: Preamble vs alternatives

## Context

The preamble feature provides context-sensitive one-liners that summarize what workflow skills do based on your project's current state and recent activity. It helps you orient yourself when switching between tasks or onboarding new team members.

## Feature comparison

| Feature | Primary use | Output format | Context awareness | Best for |
|---------|-------------|---------------|-------------------|----------|
| **preamble** | Contextual skill summaries | Single-line descriptions | Yes - adapts to project state | Quick orientation, skill discovery |
| Other help features | Static documentation | Multi-line explanations | No - same content always | Detailed learning, reference |

## When to use preamble

Use preamble when you need quick, contextual summaries of what workflow skills do:

- **Rapid task switching** — Get oriented on what a skill does without reading full documentation
- **Skill discovery** — Find related skills through `get_related_preambles()` when exploring workflow options
- **Dynamic help systems** — Build interfaces that show relevant skills based on current project context

The API provides two focused entry points:
- `get_preamble()` — Returns a one-liner description for a specific skill
- `get_related_preambles()` — Returns up to 3 related skills based on shared tags

## When NOT to use preamble

Preamble has a narrow scope that makes it unsuitable for several scenarios:

- **Detailed documentation needs** — Preambles are one-liners only; use full help features for comprehensive guides
- **Static content generation** — The context-sensitivity requires runtime calls; pre-generated docs should use other help features
- **Complex workflow orchestration** — Preambles describe individual skills but don't coordinate multi-step processes

## Recommendations

**Use preamble when** you need contextual, bite-sized descriptions that adapt to your project's current state. It excels at helping you quickly understand what skills are available and relevant right now.

**Use other help features when** you need detailed explanations, static documentation, or comprehensive guides that don't change based on context.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
