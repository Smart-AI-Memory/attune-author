---
type: quickstart
feature: template-generation
depth: quickstart
generated_at: 2026-04-11T04:47:28.090623+00:00
source_hash: c984ed6eeee4ee72f8b218ec3aebe243eb03ae557e252ba48d52da016704935e
status: generated
---

# Quickstart: template generation

```python
from attune_author.generator import generate_feature_templates
from pathlib import Path

result = generate_feature_templates(
    feature="my-feature",
    help_dir="./help",
    project_root="."
)
print(f"Generated {len(result.templates)} templates")
```

## Prerequisites

- Python environment with attune-author installed
- A project with feature definitions in your source code

## Generate your first templates

1. **Create the basic structure.** Make sure you have a help directory and your project root is accessible:

   ```python
   from attune_author.generator import generate_feature_templates
   from pathlib import Path

   # Generate templates for a specific feature
   result = generate_feature_templates(
       feature="your-feature-name",
       help_dir="./help",
       project_root="."
   )
   ```

2. **Check the output.** The function returns a `GenerationResult` with details about what was created:

   ```python
   print(f"Generated {len(result.templates)} templates")
   for template in result.templates:
       print(f"Created: {template.path}")
   ```

3. **View your generated files.** Navigate to your help directory to see the markdown templates that were created from your source code.

Expected output:
```
Generated 3 templates
Created: ./help/quickstart.md
Created: ./help/reference.md
Created: ./help/concept.md
```

**Next:** Customize your templates by modifying the generated markdown files or explore the `overwrite=True` option to regenerate existing files.
