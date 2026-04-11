---
type: task
feature: polish
depth: task
generated_at: 2026-04-11T04:48:11.796825+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Work with polish

Use the polish feature when you need to improve the quality of auto-generated documentation templates through LLM-powered rewrites.

## Prerequisites

- Access to the project source code
- Familiarity with the files under `src/attune_author/polish.py`

## Configure polish behavior

1. **Locate the polish configuration.**
   Open `src/attune_author/polish.py` to see the main polish functions.

2. **Modify the source summary generation.**
   Edit `build_source_summary()` to change what context the LLM receives about your codebase. This function controls which classes, functions, and metadata appear in the polish prompt.

3. **Update system prompts for template types.**
   Open `src/attune_author/polish_prompts.py` and modify `get_system_prompt()` to adjust polish instructions for specific template types (task, concept, reference, etc.).

## Polish a template

1. **Call the polish function.**
   Use `polish_template()` with your generated template content:
   ```python
   polished = polish_template(
       content=raw_template,
       feature_name="your_feature",
       source_summary=summary,
       template_type="task"
   )
   ```

2. **Handle polish failures.**
   Catch `PolishError` exceptions when running in strict mode to handle cases where the LLM polish fails.

3. **Verify the output.**
   Check that the polished template maintains the original YAML frontmatter and preserves the core structure while improving readability and clarity.

## Test your changes

Run targeted tests to verify polish behavior:
```bash
pytest -k "polish"
```

The tests pass when your polish modifications correctly transform templates without breaking the original structure or losing essential information.

## Key files

- `src/attune_author/polish.py` — Main polish functions
- `src/attune_author/polish_prompts.py` — Template-specific system prompts
