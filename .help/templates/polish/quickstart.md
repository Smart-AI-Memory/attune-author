---
type: quickstart
feature: polish
depth: quickstart
generated_at: 2026-04-14T14:00:42.037905+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Quickstart: polish

```python
from attune_author.polish import polish_template

# Polish a basic template
polished = polish_template(
    content="# My Feature\nBasic template content here.",
    feature_name="my-feature",
    source_summary="A simple example module with one function.",
    template_type="quickstart"
)
print(polished)
```

## Prerequisites

- Python environment with attune_author installed
- API access configured for the LLM service

## Steps

1. **Prepare your template content.** Start with a generated template string that needs improvement.

2. **Create a source summary.** Use `build_source_summary()` to describe your module's public API, or write a brief summary manually.

3. **Run the polish pass.** Call `polish_template()` with your content, feature name, source summary, and template type.

## Expected output

The function returns a polished markdown string with improved clarity, structure, and adherence to documentation standards. Error handling follows Google's style guide, and technical accuracy is preserved from your source summary.

If the polish pass fails in strict mode, you'll see a `PolishError` with details about what went wrong.

## Next steps

Review the polished output and integrate it into your documentation workflow. For error handling and advanced configuration options, see the polish reference documentation.
