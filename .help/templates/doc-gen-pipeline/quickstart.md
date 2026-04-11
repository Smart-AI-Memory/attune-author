---
type: quickstart
feature: doc-gen-pipeline
depth: quickstart
generated_at: 2026-04-11T05:01:31.827116+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Quickstart: doc gen pipeline

```python
from attune_author.doc_gen.pipeline import generate_docs

result = generate_docs("path/to/your/source.py")
print(result.content)
```

This command runs the complete three-stage pipeline (outline, write, review) to generate documentation for any source file.

## Generate your first documentation

1. **Create a simple Python file** to document:
   ```python
   # example.py
   def hello(name):
       """Say hello to someone."""
       return f"Hello, {name}!"
   ```

2. **Run the pipeline** on your file:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs

   result = generate_docs("example.py")
   print(result.content)
   ```

3. **View the generated documentation**. You should see structured documentation that includes function descriptions, parameters, and usage examples based on your source code.

## Expected output

The pipeline returns a `DocGenResult` object containing polished documentation. For the example above, you'll see:
- A clear description of the `hello` function
- Parameter documentation for `name`
- Return value details
- Potentially usage examples

## Next steps

Customize your documentation output by configuring the `DocGenConfig` class to specify document type, target audience, and output format preferences.
