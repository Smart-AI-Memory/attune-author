---
type: task
feature: template-generation
depth: task
generated_at: 2026-04-11T04:46:34.079276+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Work with template generation

Use template generation when you need to create markdown help files from your codebase's feature definitions and source code analysis.

## Prerequisites

- Access to the project source code
- Python development environment set up

## Generate templates for a feature

1. **Import the generator module:**
   ```python
   from attune_author.generator import generate_feature_templates
   ```

2. **Prepare the required parameters:**
   - Feature object containing your feature definition
   - Path to your help directory where templates will be written
   - Path to your project root for source code analysis

3. **Call the generation function:**
   ```python
   result = generate_feature_templates(
       feature=your_feature,
       help_dir="docs/help",
       project_root=".",
       overwrite=True  # Set to False to preserve existing files
   )
   ```

4. **Check the generation result:**
   The function returns a `GenerationResult` object containing details about created templates.

## Verify template generation

- Check that new markdown files appear in your specified help directory
- Verify each generated template contains proper YAML frontmatter
- Confirm template content reflects your source code structure
- Run `pytest -k "template-generation"` to validate the generation process

## Key files

- `src/attune_author/generator.py` — Core template generation logic
