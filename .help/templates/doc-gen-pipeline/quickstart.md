---
type: quickstart
feature: doc-gen-pipeline
depth: quickstart
generated_at: 2026-04-14T16:19:24.051817+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Quickstart: doc gen pipeline

```python
from attune_author.doc_gen.pipeline import generate_docs

result = generate_docs("src/my_module.py")
print(result.content)
```

## Set up your API key

The pipeline uses Anthropic's Claude model. Install the AI dependencies and set your API key:

```bash
pip install 'attune-author[ai]'
export ANTHROPIC_API_KEY="your-key-here"
```

## Generate documentation

Run the pipeline on any Python source file:

```python
from attune_author.doc_gen.pipeline import generate_docs, DocGenConfig

# Basic usage with defaults
result = generate_docs("src/my_module.py")

# Custom configuration
config = DocGenConfig(
    doc_type="tutorial",
    audience="beginners",
    max_write_tokens=12000
)
result = generate_docs("src/my_module.py", config=config)

# Save output to file
result = generate_docs("src/my_module.py", output_path="docs/my_module.md")
```

## Check the output

The result contains the complete documentation and intermediate stages:

```python
print("Final content:", result.content[:200] + "...")
print("Outline:", result.outline[:100] + "...")
print("Stages completed:", result.stages_completed)
# Output: ['outline', 'write', 'review']
```

**Next:** Configure the pipeline with `DocGenConfig` to customize document type, audience, and token limits for your project's needs.
