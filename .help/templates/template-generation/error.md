---
type: error
feature: template-generation
depth: error
generated_at: 2026-04-14T16:02:45.849618+00:00
source_hash: 83bb6e5c2f6907087e0db48de07d88ae3c21652d99c4be4964d15c1658289845
status: generated
---

# Template Generation errors

Template generation failures occur when creating help documentation templates from source code analysis and feature definitions.

## Common error signatures

- `ValueError: Invalid feature name: {name}` — The feature name you provided doesn't match any recognized feature in the project

## Where errors originate

Template generation errors stem from the main generation function:

- `generate_feature_templates()` in `src/attune_author/generator.py` — Orchestrates template creation for a feature, validating inputs and coordinating file operations

## How to diagnose

1. **Verify the feature name.** If you see "Invalid feature name", check that your feature identifier matches one defined in your project's feature registry. Feature names are case-sensitive and must exactly match the registered identifier.

2. **Check file permissions.** Template generation writes to the help directory. Ensure you have write access to the target directory and that no files are locked by other processes.

3. **Validate source file integrity.** The generation process analyzes source files to extract documentation patterns. If source files have syntax errors or are corrupted, generation may fail during AST parsing.

4. **Examine the generation result.** The `GenerationResult` object contains diagnostic information including `matched_files` and `source_hash`. Empty `matched_files` indicates the feature finder couldn't locate relevant source files.

## Source files

- `src/attune_author/generator.py`

**Tags:** `generation`, `jinja2`, `ast`, `meta-templates`
