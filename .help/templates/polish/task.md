---
type: task
feature: polish
depth: task
generated_at: 2026-04-14T13:59:30.435223+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Work with polish

Use the polish feature when you need to improve auto-generated help templates with LLM-powered rewrites that apply template-specific style rules and source-accurate content.

## Prerequisites

- Access to the project source code
- Python environment with the polish module available

## Identify the polish function you need

1. **Review the available functions** in `src/attune_author/polish.py`:
   - `polish_template()` — Improves template content using LLM rewriting
   - `build_source_summary()` — Creates source summaries for the LLM context
   - `get_system_prompt()` — Retrieves template-specific style prompts

2. **Check function signatures** to confirm parameters and return types match your use case.

## Polish a template

1. **Prepare your inputs:**
   - Template content as a string
   - Feature name the template documents
   - Source summary from `build_source_summary()`
   - Template type (defaults to 'generic')

2. **Call `polish_template()`:**
   ```python
   polished_content = polish_template(
       content=template_string,
       feature_name="your_feature",
       source_summary=summary,
       template_type="task"  # or "reference", "explanation", etc.
   )
   ```

3. **Handle `PolishError` exceptions** when `strict=True` mode is enabled.

## Build source summaries

1. **Collect source information:**
   - Public classes with their purposes
   - Public functions with signatures and descriptions
   - Module docstrings
   - File count

2. **Create the summary:**
   ```python
   summary = build_source_summary(
       public_classes=class_list,
       public_functions=function_list,
       module_docstrings=docstring_list,
       file_count=total_files
   )
   ```

## Test your changes

Run targeted tests to verify polish functionality:
```bash
pytest -k "polish"
```

## Verify success

Your polish operation succeeds when:
- The returned content maintains the original YAML frontmatter
- Template structure follows the specified type's style guide
- All source information remains factually accurate
- No `PolishError` is raised in strict mode
