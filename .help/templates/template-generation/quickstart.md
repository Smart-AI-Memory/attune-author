---
type: quickstart
feature: template-generation
depth: quickstart
generated_at: 2026-04-14T16:03:33.702532+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Quickstart: template generation

```python
from attune_author.generator import generate_feature_templates
from pathlib import Path

# Generate templates for a feature
result = generate_feature_templates(
    feature="my-feature",
    help_dir="./docs",
    project_root="."
)
print(f"Generated {len(result.templates)} templates")
```

## Create your first templates

1. **Define your feature name** and call `generate_feature_templates()` with the required paths:

   ```python
   result = generate_feature_templates(
       feature="user-auth",
       help_dir="./help",
       project_root="./src"
   )
   ```

2. **Check what was generated** by examining the result:

   ```python
   for template in result.templates:
       print(f"Created: {template.path} (depth: {template.depth})")
   ```

   Expected output:
   ```
   Created: ./help/user-auth/quickstart.md (depth: quickstart)
   Created: ./help/user-auth/concept.md (depth: concept)
   Created: ./help/user-auth/reference.md (depth: reference)
   ```

3. **Verify the templates** exist on disk at the paths shown in `template.path`.

**Next:** Run the generator with `overwrite=True` to update existing templates when your source code changes.
