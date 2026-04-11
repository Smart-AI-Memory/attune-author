---
type: quickstart
feature: polish
depth: quickstart
generated_at: 2026-04-11T04:49:16.955821+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Quickstart: polish

```python
from attune_author.polish import polish_template

# Polish a basic template
polished = polish_template(
    content="# Help: myfeature\n\nThis explains myfeature.",
    feature_name="myfeature",
    source_summary="Functions: do_thing() - Does a thing",
    template_type="reference"
)
print(polished)
```

## Prerequisites

- Python environment with the attune-author package installed
- API access configured for the LLM service

## Steps

1. **Prepare your source summary.** Use `build_source_summary()` to create a concise description of your code:

   ```python
   from attune_author.polish import build_source_summary

   summary = build_source_summary(
       public_classes=[{"name": "MyClass", "purpose": "Handles data"}],
       public_functions=[{"name": "process", "purpose": "Processes input"}],
       module_docstrings=["Main processing module"],
       file_count=3
   )
   ```

2. **Polish your template.** Call `polish_template()` with your raw template content:

   ```python
   polished_content = polish_template(
       content=raw_template,
       feature_name="myfeature",
       source_summary=summary,
       template_type="quickstart"  # or "reference", "concept", etc.
   )
   ```

3. **Review the output.** The polished template follows Google's developer documentation style with improved clarity and structure.

Expected output: A rewritten template with active voice, second person perspective, and template-specific improvements based on the type you specified.

**Next:** Read the reference documentation to understand all available template types and polish options.
