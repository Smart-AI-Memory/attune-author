---
type: task
feature: template-generation
depth: task
generated_at: 2026-04-26T19:46:35.990000+00:00
source_hash: e3ad2679109ec5bb81db1607254855a0f32feadedbce291531797eb11bf09912
status: generated
---

# Work with template generation

Use template generation when you need to create markdown help templates from feature definitions and source code analysis.

## Prerequisites

- Access to the project source code
- Understanding of the `src/attune_author/generator.py` module structure

## Generate templates for a feature

1. **Import the generation function**
   ```python
   from attune_author.generator import generate_feature_templates
   ```

2. **Define your feature and paths**
   ```python
   feature = Feature(name="your-feature-name")
   help_dir = Path("help")
   project_root = Path(".")
   ```

3. **Call the generator with your parameters**
   ```python
   result = generate_feature_templates(
       feature=feature,
       help_dir=help_dir,
       project_root=project_root,
       depths=["concept", "task", "reference"],  # optional
       overwrite=False,  # optional
       use_rag=True  # optional
   )
   ```

4. **Check the generation result**
   ```python
   print(f"Generated {len(result.templates)} templates for {result.feature}")
   for template in result.templates:
       print(f"- {template.depth}: {template.path}")
   ```

## Modify template generation behavior

1. **Locate the function you need to change**
   Open `src/attune_author/generator.py` and find `generate_feature_templates()`. This function orchestrates the entire generation process.

2. **Review the current implementation**
   Read the function's docstring, parameters, and return type to understand its responsibilities before making changes.

3. **Follow the existing patterns**
   Use the same naming conventions, error handling style (raising `ValueError` for invalid feature names), and return type structure (`GenerationResult`) as the current code.

4. **Test your changes**
   Run the template generation tests to verify your modifications work correctly:
   ```bash
   pytest -k "template-generation"
   ```

## Verify template generation worked

After running `generate_feature_templates()`, you should see:
- A `GenerationResult` object with the correct feature name
- Template files created at the specified paths in the help directory
- Each generated template has a unique `source_hash` matching the input
- The `matched_files` list contains the source files that were analyzed

The generation succeeds when all specified depths produce valid markdown files with proper YAML frontmatter.
