---
type: comparison
feature: template-generation
depth: comparison
generated_at: 2026-04-14T13:59:05.608264+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template generation vs manual help authoring

## Context

You need to create help documentation for your codebase. You can either generate templates automatically from source code inspection or write documentation manually from scratch.

## Feature comparison

| Aspect | Template generation | Manual authoring |
|--------|-------------------|------------------|
| **Speed** | Fast bulk creation of structured templates | Slower, write each page individually |
| **Consistency** | Enforced template structure across all docs | Varies by author, requires style guides |
| **Accuracy** | Auto-synced with source code via AST inspection | Manual updates required when code changes |
| **Customization** | Limited to template variables and depth types | Full control over content and structure |
| **Maintenance** | Regenerate when code changes | Manual review and updates needed |
| **Learning curve** | Requires understanding feature definitions | Standard markdown writing skills |

## Template generation capabilities

Template generation creates structured help files by analyzing your source code's abstract syntax tree (AST). It produces three depth types:

- **concept**: High-level explanations
- **task**: Step-by-step procedures
- **reference**: Detailed API documentation

And four problem-solving templates:

- **error**: Error message explanations
- **warning**: Warning resolution guides
- **troubleshooting**: Diagnostic procedures
- **faq**: Common questions

The `generate_feature_templates()` function handles the entire process, creating multiple template files for each feature based on your source code structure.

## Use template generation when...

- You have multiple features that need consistent documentation structure
- Your codebase changes frequently and you want docs to stay in sync
- You prefer structured, template-driven documentation over free-form writing
- You want to bootstrap documentation quickly and polish the generated content later
- Your team values consistency over creative formatting

## Use manual authoring when...

- You need complete control over documentation structure and style
- Your content includes extensive conceptual explanations not reflected in source code
- You're documenting workflows that span multiple codebases
- You prefer writing documentation as part of your design process
- Your documentation needs custom formatting that doesn't fit standard templates

## Recommendation

Start with template generation to establish consistent structure and coverage, then manually enhance the generated content. The auto-generated templates provide scaffolding that ensures you don't miss important topics while giving you a foundation to build more detailed explanations.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
