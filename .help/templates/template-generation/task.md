---
type: task
feature: template-generation
depth: task
generated_at: 2026-04-14T16:02:30.330557+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Work with template generation

Use template generation when you need to create markdown help templates automatically from your feature definitions and source code analysis.

## Prerequisites

- Access to the project source code
- Familiarity with `src/attune_author/generator.py`

## Generate templates for a feature

1. **Import the generation function:**
   ```python
   from attune_author.generator import generate_feature_templates
   ```

2. **Call the function with your feature:**
   ```python
   result = generate_feature_templates(
       feature=your_feature,
       help_dir="docs/help",
       project_root=".",
       depths=["concept", "task", "reference"],  # Optional
       overwrite=False  # Optional
   )
   ```

3. **Check the generation result:**
   ```python
   print(f"Generated {len(result.templates)} templates for {result.feature}")
   for template in result.templates:
       print(f"  {template.depth}: {template.path}")
   ```

## Verify template generation

Check that templates were created successfully:

- Generated template files exist at the specified paths in `result.templates`
- Each template has valid YAML frontmatter with correct `feature`, `depth`, and `source_hash` fields
- Template content matches the structure for its depth type (concept, task, reference, etc.)

## Handle generation errors

If `generate_feature_templates()` raises a `ValueError` with "Invalid feature name:", verify:

- Your feature object has a valid name attribute
- The feature name contains only allowed characters
- Required feature properties are properly set

## Key files

- `src/attune_author/generator.py` — Main template generation logic
