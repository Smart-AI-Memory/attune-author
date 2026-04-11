---
type: task
feature: doc-gen-pipeline
depth: task
generated_at: 2026-04-11T05:00:20.078968+00:00
source_hash: dcd99211b2080853c45dbe17f061733f0b7ff80387279d574d2bd011d8114aa2
status: generated
---

# Work with doc gen pipeline

Use the doc gen pipeline when you need to generate high-quality documentation through a three-stage process that creates an outline, writes content, and reviews the output.

## Prerequisites

- Access to the project source code
- Familiarity with the files under `src/attune_author/doc_gen/`

## Generate documentation

1. **Import the pipeline module.**
   ```python
   from attune_author.doc_gen.pipeline import generate_docs
   from attune_author.doc_gen.config import DocGenConfig
   ```

2. **Configure the generation settings.**
   Create a `DocGenConfig` object with your target audience, document type, and model preferences:
   ```python
   config = DocGenConfig(
       doc_type="tutorial",
       audience="developers",
       model="gpt-4",
       max_tokens=2000
   )
   ```

3. **Run the generation pipeline.**
   Call `generate_docs()` with your source file or content:
   ```python
   result = generate_docs("path/to/source.py", config, "output/docs.md")
   ```

4. **Verify the output.**
   Check that the result contains structured documentation with outline, content, and review stages completed. The output file should contain polished documentation that follows the specified format.

## Customize individual stages

1. **Import the stage functions.**
   ```python
   from attune_author.doc_gen.stages import build_outline, write_content, review_content
   ```

2. **Generate a custom outline.**
   Use `build_outline()` to create a structured plan before writing:
   ```python
   outline = build_outline(client, source_content, "api-reference", "developers", "gpt-4", 1000)
   ```

3. **Write focused content.**
   Use `write_content()` with specific section focus to target particular areas:
   ```python
   content = write_content(client, outline, source_content, "tutorial", "beginners", "gpt-4", 2000, ["setup", "examples"])
   ```

4. **Review and polish.**
   Use `review_content()` to improve the initial draft:
   ```python
   final_content = review_content(client, draft, source_content, "guide", "experts", "gpt-4", 1500)
   ```

## Test your changes

Run the pipeline tests to verify your modifications work correctly:
```bash
pytest -k "doc-gen-pipeline"
```

Success indicators include passing tests and generated documentation that follows the expected three-stage structure.

## Key files

- `src/attune_author/doc_gen/pipeline.py` — Main orchestration and `generate_docs()` function
- `src/attune_author/doc_gen/stages.py` — Individual pipeline stages
- `src/attune_author/doc_gen/config.py` — Configuration classes
