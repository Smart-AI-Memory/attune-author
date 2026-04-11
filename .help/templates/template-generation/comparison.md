---
type: comparison
feature: template-generation
depth: comparison
generated_at: 2026-04-11T04:47:47.861318+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Template Generation vs Manual Documentation

## Context

Template generation automatically creates markdown help files by analyzing your source code's AST and feature definitions. This approach competes with writing documentation manually or using simpler code-to-docs tools.

## Feature comparison

| Aspect | Template Generation | Manual Documentation | Generic Doc Generators |
|--------|-------------------|---------------------|----------------------|
| **Accuracy** | Synced to actual code via AST | Prone to drift | Basic reflection only |
| **Customization** | Jinja2 templates + feature metadata | Full control | Limited templates |
| **Maintenance** | Regenerate when code changes | Manual updates required | Regenerate but shallow |
| **Structure** | Enforced consistency across features | Varies by author | Basic structure only |
| **Setup cost** | Feature definitions + template setup | None | Minimal |
| **Content depth** | Code + curated feature context | Unlimited | Function signatures only |

## Use template generation when

- You have multiple features that need consistent documentation structure
- Your code changes frequently and you want docs that stay current
- You want to enforce documentation standards across a team
- You need both API reference and conceptual content from the same source

The `generate_feature_templates()` function is designed for projects where documentation quality and consistency matter more than setup speed.

## Use manual documentation when

- Your project has fewer than 5 features or modules
- You need extensive narrative content that doesn't map to code structure
- Your documentation requirements are highly specialized
- You prefer full editorial control over automated consistency

## Use generic doc generators when

- You only need API reference documentation
- Your codebase is stable and rarely changes
- You want zero configuration overhead
- Simple docstring extraction meets your needs

## Recommendation

Choose template generation if you're building a multi-feature project where documentation quality directly impacts user success. The upfront cost of defining features and templates pays off when you need to maintain dozens of help files that stay accurate as your code evolves.

For smaller projects or one-off documentation needs, manual writing is usually faster and simpler.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
