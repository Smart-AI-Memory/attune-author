---
type: task
feature: polish
depth: task
generated_at: 2026-04-14T16:04:20.634263+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Work with polish

Use polish when you need to improve auto-generated documentation templates through AI-powered rewriting that applies template-specific writing rules and incorporates source code context.

## Prerequisites

- Access to the project source code
- Familiarity with the files under `src/attune_author/polish.py`

## Configure polish behavior

1. **Set strict mode for error handling.**
   Control whether polish failures raise exceptions:
   ```python
   # Raise PolishError on failures
   polish_template(content, feature_name, source_summary, strict=True)

   # Return original content on failures
   polish_template(content, feature_name, source_summary, strict=False)
   ```

2. **Choose the appropriate template type.**
   Select from available system prompts:
   ```python
   # For task-oriented documentation
   polish_template(content, feature_name, source_summary, template_type='task')

   # For reference documentation
   polish_template(content, feature_name, source_summary, template_type='reference')
   ```

## Polish a template

1. **Build a source summary.**
   Create context for the LLM using your code analysis:
   ```python
   from attune_author.polish import build_source_summary

   summary = build_source_summary(
       public_classes=[{'name': 'PolishError', 'purpose': 'Raised when polish fails'}],
       public_functions=[{'name': 'polish_template', 'purpose': 'Polish generated template'}],
       module_docstrings=['LLM polish pass for generated help templates'],
       file_count=2
   )
   ```

2. **Apply the polish pass.**
   Transform your generated template:
   ```python
   from attune_author.polish import polish_template

   polished = polish_template(
       content=raw_template,
       feature_name="polish",
       source_summary=summary,
       template_type="task"
   )
   ```

3. **Handle polish errors.**
   Catch and respond to polish failures:
   ```python
   from attune_author.polish import PolishError

   try:
       polished = polish_template(content, feature_name, summary, strict=True)
   except PolishError as e:
       print(f"Polish failed: {e}")
       # Fall back to original content
   ```

## Verify polish results

Check that the polished template meets quality standards:

- **Content preservation**: Original technical information remains accurate
- **Style improvements**: Text follows Google's developer documentation style
- **Template compliance**: Output matches the expected template type structure
- **Error-free processing**: No `PolishError` exceptions in strict mode

## Key files

- `src/attune_author/polish.py` — Core polish functions and error handling
- `src/attune_author/polish_prompts.py` — Template-specific system prompts
