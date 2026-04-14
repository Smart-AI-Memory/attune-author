---
type: comparison
feature: template-generation
depth: comparison
generated_at: 2026-04-14T16:03:57.430391+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template generation vs manual documentation

## Context

Template generation automatically creates structured help files by analyzing your codebase and feature definitions. It extracts function signatures, class fields, and module purposes to populate markdown templates with accurate, up-to-date information.

## Feature comparison

| Aspect | Template generation | Manual documentation |
|--------|-------------------|---------------------|
| **Accuracy** | Always matches current code via AST inspection | Can drift from implementation |
| **Speed** | Generates multiple templates in seconds | Hours per comprehensive feature |
| **Consistency** | Enforces uniform structure across all features | Varies by author style and attention |
| **Customization** | Limited to predefined template types | Complete control over content and format |
| **Maintenance** | Regenerates automatically when code changes | Requires manual updates for every change |
| **Learning curve** | Requires understanding of feature definitions | Uses familiar markdown editing |

## Template types available

Template generation supports three depth categories:

- **Core depths**: `concept`, `task`, `reference` — fundamental documentation types
- **Problem-solving**: `error`, `warning`, `troubleshooting`, `faq` — help users resolve issues
- **Guidance**: `quickstart`, `tip`, `note`, `comparison` — orient and advise users

## Use template generation when

- You need comprehensive documentation for multiple features quickly
- Your team struggles to keep docs synchronized with code changes
- You want consistent structure across all help content
- You have well-defined features in your `.help/features.yaml`
- Accuracy matters more than prose perfection

## Use manual documentation when

- You need highly customized explanations that don't fit standard templates
- Your content requires extensive narrative or storytelling
- You're documenting concepts that span multiple features
- You need one-off documentation for experimental features
- Your audience needs marketing-style copy rather than technical reference

## Recommended approach

Start with template generation for comprehensive coverage, then manually enhance the generated files where your users need more guidance. The generated templates provide accurate scaffolding that you can polish with context, examples, and clearer explanations.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
