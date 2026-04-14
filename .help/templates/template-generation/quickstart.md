---
type: quickstart
feature: template-generation
depth: quickstart
generated_at: 2026-04-14T13:58:44.063661+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Quickstart: template generation

```python
from attune_author.generator import generate_feature_templates
from pathlib import Path

# Generate templates for a feature called "my-feature"
result = generate_feature_templates(
    feature="my-feature",
    help_dir="docs/help",
    project_root="."
)

print(f"Generated {len(result.templates)} templates")
for template in result.templates:
    print(f"  {template.path}")
```

## Generate your first template

1. **Create a feature definition** in your project that describes what you want to document.

2. **Run the generator** with your feature name and output directory:
   ```python
   result = generate_feature_templates(
       feature="your-feature-name",
       help_dir="docs/help",
       project_root="."
   )
   ```

3. **Check the output** to see what templates were created:
   ```python
   print(f"Created templates for {result.feature}:")
   for template in result.templates:
       print(f"  {template.depth}: {template.path}")
   ```

You should see output showing the generated template files and their locations in your help directory.

## Next

Read the concept page for template-generation to understand how the AST inspection and template rendering process works.
