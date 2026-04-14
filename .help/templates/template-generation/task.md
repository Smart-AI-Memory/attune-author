---
type: task
feature: template-generation
depth: task
generated_at: 2026-04-14T13:57:44.082676+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Work with template generation

Use template generation when you need to create markdown help templates automatically from feature definitions and source code analysis.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/generator.py`

## Generate templates for a feature

1. **Import the generation function**
   ```python
   from attune_author.generator import generate_feature_templates
   ```

2. **Call the function with your feature**
   ```python
   from pathlib import Path

   result = generate_feature_templates(
       feature=your_feature,
       help_dir="docs/help",
       project_root=".",
       depths=["concept", "task", "reference"],  # Optional
       overwrite=False  # Set True to replace existing files
   )
   ```

3. **Check the generation result**
   ```python
   print(f"Generated {len(result.templates)} templates for {result.feature}")
   for template in result.templates:
       print(f"  {template.depth}: {template.path}")
   ```

## Verify successful generation

- Check that `result.templates` contains the expected template types
- Confirm the generated files exist at the specified paths
- Verify each template has a valid `source_hash` that matches the current codebase

## Key components

The generation process creates:
- **Core templates**: concept, task, and reference documentation
- **Problem templates**: error, warning, troubleshooting, and FAQ guides
- **Guidance templates**: quickstart, tip, note, and comparison content

Each generated template includes metadata about the source feature and creation timestamp.
