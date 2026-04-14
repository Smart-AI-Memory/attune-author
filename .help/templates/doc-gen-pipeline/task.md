---
type: task
feature: doc-gen-pipeline
depth: task
generated_at: 2026-04-14T14:13:06.541299+00:00
source_hash: 6474cc0d69cd0c4e82d4326b3b640d5a2a68fcfc45b228e045a8cca9f9c93b0b
status: generated
---

# Work with doc gen pipeline

Use the document generation pipeline when you need to create structured, high-quality documentation through a three-stage process of outlining, writing, and reviewing content.

## Prerequisites

- Access to the project source code
- Anthropic API credentials (install with `pip install 'attune-author[ai]'`)
- Python source file or content to document

## Generate documentation with default settings

1. **Call the main pipeline function**:
   ```python
   from attune_author.doc_gen.pipeline import generate_docs

   result = generate_docs("path/to/source.py")
   ```

2. **Access the generated content**:
   ```python
   print(result.content)  # Final documentation
   print(result.outline)  # Generated outline
   print(result.draft)    # Draft before review
   ```

## Configure the generation process

1. **Create a custom configuration**:
   ```python
   from attune_author.doc_gen.pipeline import DocGenConfig, generate_docs

   config = DocGenConfig(
       doc_type="tutorial",
       audience="beginners",
       max_write_tokens=12000,
       section_focus=["examples", "troubleshooting"]
   )
   ```

2. **Generate with custom settings**:
   ```python
   result = generate_docs("source.py", config=config, output_path="docs/output.md")
   ```

## Modify individual pipeline stages

1. **Import the stage functions**:
   ```python
   from attune_author.doc_gen.stages import build_outline, write_content, review_content
   from anthropic import Anthropic
   ```

2. **Run a single stage**:
   ```python
   client = Anthropic()
   source_content = "# Your source code here"

   outline = build_outline(
       client=client,
       source_content=source_content,
       doc_type="api-reference",
       audience="developers",
       model="claude-sonnet-4-20250514",
       max_tokens=1000
   )
   ```

3. **Chain stages manually**:
   ```python
   draft = write_content(client, outline, source_content, "api-reference", "developers", "claude-sonnet-4-20250514", 8000)
   final_content = review_content(client, draft, source_content, "api-reference", "developers", "claude-sonnet-4-20250514", 8000)
   ```

## Verify successful generation

Check that the `DocGenResult` contains the expected stages:
```python
assert "outline" in result.stages_completed
assert "write" in result.stages_completed
assert "review" in result.stages_completed
assert len(result.content) > 0
```

Your documentation generation succeeds when all three stages complete and `result.content` contains structured documentation matching your specified format and audience.
