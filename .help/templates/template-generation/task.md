---
type: task
feature: template-generation
depth: task
generated_at: 2026-04-12T04:18:08.689196+00:00
source_hash: fac9c2bf60f422bb00b839a6c2ae022747745371b4a85621dd89daba9515f706
status: generated
---

# Generate help templates from source code

Use template generation when you need to create markdown help files automatically from feature definitions and source code analysis.

## Prerequisites

- Access to the project source code
- Python development environment with pytest installed

## Generate templates for a feature

1. **Import the generation function:**
   ```python
   from attune_author.generator import generate_feature_templates
   ```

2. **Define your feature and paths:**
   ```python
   result = generate_feature_templates(
       feature=your_feature,
       help_dir="docs/help",
       project_root=".",
       depths=["overview", "task", "reference"],
       overwrite=True
   )
   ```

3. **Check the generation results:**
   The function returns a `GenerationResult` containing:
   - List of successfully generated templates
   - Any errors encountered during generation
   - File paths for each created template

## Verify template generation

Run the test suite to confirm your templates generate correctly:

```bash
pytest -k "template-generation"
```

**Success criteria:** All tests pass and you can find the generated markdown files in your specified help directory. Each template should have proper YAML frontmatter and structured content based on your source code.

## Key files

- `src/attune_author/generator.py` — Core template generation logic
