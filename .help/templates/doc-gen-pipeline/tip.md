---
type: tip
feature: doc-gen-pipeline
depth: tip
generated_at: 2026-04-14T16:19:31.756172+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Set section_focus to control what the pipeline emphasizes

## Recommendation

Use the `section_focus` field in `DocGenConfig` to direct the pipeline's attention to specific documentation sections. This three-stage process (outline → write → review) works best when you tell it what matters most for your particular source code.

```python
config = DocGenConfig(
    doc_type='api-reference',
    section_focus=['error-handling', 'configuration', 'examples']
)
generate_docs('my_module.py', config)
```

## Why this helps

The LLM has limited tokens across all three stages, so unfocused generation often produces generic content that misses your code's key concepts.

## The tradeoff

More focused documentation means less coverage of edge cases and secondary features — you get depth at the expense of breadth.
