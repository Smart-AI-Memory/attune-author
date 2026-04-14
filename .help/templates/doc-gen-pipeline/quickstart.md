---
type: quickstart
feature: doc-gen-pipeline
depth: quickstart
generated_at: 2026-04-14T14:14:28.916629+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Quickstart: doc gen pipeline

```python
from attune_author.doc_gen.pipeline import generate_docs

result = generate_docs("path/to/your/source.py")
print(result.content)
```

## Generate your first document

1. **Install the AI dependencies** if you haven't already:
   ```bash
   pip install 'attune-author[ai]'
   ```

2. **Run the pipeline** on a source file:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs

   result = generate_docs("src/my_module.py")
   print(f"Generated {len(result.content)} characters of documentation")
   ```

3. **Check the output**. The pipeline completes three stages (outline, write, review) and returns a `DocGenResult` with the final documentation in `result.content`.

## Expected output

```
Generated 2847 characters of documentation
Stages completed: ['outline', 'write', 'review']
```

The `result.content` field contains your generated documentation, while `result.stages_completed` confirms all three pipeline stages ran successfully.

**Next:** Save the documentation to a file by adding `output_path="docs/my_module.md"` to your `generate_docs()` call.
