---
type: quickstart
feature: polish
depth: quickstart
generated_at: 2026-04-14T16:05:37.365780+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Quickstart: polish

Polish a generated template with one function call:

```python
from attune_author.polish import polish_template

# Polish an auto-generated template
polished = polish_template(
    content="# My Template\n\nThis is a draft template.",
    feature_name="my_feature",
    source_summary="Module for user authentication with login() and logout() functions",
    template_type="quickstart"
)

print(polished)
```

## Prerequisites

- Python environment with attune_author installed
- Generated template content to polish

## Steps

1. **Import the polish function**
   ```python
   from attune_author.polish import polish_template
   ```

2. **Build your source summary** (or use an existing one)
   ```python
   from attune_author.polish import build_source_summary

   summary = build_source_summary(
       public_classes=[],
       public_functions=[{"name": "login", "signature": "login(username, password)"}],
       module_docstrings=["Handles user authentication"],
       file_count=1
   )
   ```

3. **Polish your template**
   ```python
   result = polish_template(
       content=your_template_text,
       feature_name="auth",
       source_summary=summary,
       template_type="quickstart"
   )
   ```

Expected output: A rewritten version of your template following documentation style guidelines, with improved clarity and structure while preserving all original functionality.

## Next

Try polishing different template types by changing the `template_type` parameter to "concept" or "reference".
