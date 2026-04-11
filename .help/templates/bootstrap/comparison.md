---
type: comparison
feature: bootstrap
depth: comparison
generated_at: 2026-04-11T04:53:01.491703+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Bootstrap vs manual manifest creation

## Context

When starting a new project, you need a feature manifest that defines your project's structure. You have two approaches: use the bootstrap scanner to generate proposals automatically, or create the manifest by hand.

## Feature comparison

| Aspect | Bootstrap scanner | Manual creation |
|--------|------------------|-----------------|
| **Setup time** | ~30 seconds to scan and review | 15-60 minutes depending on project size |
| **Accuracy** | Catches standard Python patterns reliably | Perfect for your specific needs |
| **Customization** | Generates proposals you then modify | Full control from the start |
| **Learning curve** | Minimal — review and accept/reject | Requires understanding manifest format |
| **Maintenance** | Re-scan when structure changes | Update by hand when structure changes |

## Use bootstrap when

- **Starting fresh**: You have an existing Python project but no feature manifest yet
- **Following conventions**: Your project uses standard Python package layouts that the scanner recognizes
- **Want speed**: You prefer to review generated proposals rather than write from scratch
- **Exploring structure**: You're not sure what features your project needs and want suggestions

The scanner works best on projects with clear directory boundaries and conventional Python packaging.

## Use manual creation when

- **Non-standard layout**: Your project structure doesn't match typical Python patterns
- **Specific requirements**: You need exact control over feature definitions from the start
- **Small scope**: You're creating a simple manifest with just 2-3 features
- **Learning the system**: You want to understand the manifest format in detail

Manual creation gives you precise control but requires more upfront knowledge of the manifest schema.

## Recommended workflow

1. **Start with bootstrap**: Run `scan_project()` to get initial proposals
2. **Review and modify**: Accept useful proposals, reject irrelevant ones
3. **Convert to manifest**: Use `proposals_to_manifest()` to create your starting point
4. **Refine manually**: Edit the generated manifest to match your exact needs

This hybrid approach combines the speed of automation with the precision of manual tuning.

## Source files

- `src/attune_author/bootstrap.py`

**Tags:** `setup`, `scanning`, `manifest`
