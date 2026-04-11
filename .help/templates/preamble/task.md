---
type: task
feature: preamble
depth: task
generated_at: 2026-04-11T04:55:27.164476+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Work with preamble

Use preamble when you need to display contextual one-liner descriptions for workflow features or find related features based on shared functionality.

## Prerequisites

- Access to the project source code
- Python development environment set up

## Retrieve a feature preamble

1. **Import the preamble module:**
   ```python
   from attune_author.preamble import get_preamble
   ```

2. **Call get_preamble with the feature name:**
   ```python
   preamble_text = get_preamble("your_feature_name")
   ```

3. **Handle the result:**
   - If the feature exists, you get a string with the preamble text
   - If the feature doesn't exist, you get `None`

## Find related features

1. **Import the related preambles function:**
   ```python
   from attune_author.preamble import get_related_preambles
   ```

2. **Get related features by shared tags:**
   ```python
   related = get_related_preambles("your_feature_name", max_results=3)
   ```

3. **Process the results:**
   The function returns a list of dictionaries, each containing feature information for related features.

## Modify preamble functionality

1. **Locate the target function in `src/attune_author/preamble.py`:**
   - Use `get_preamble()` to change how individual preambles are retrieved
   - Use `get_related_preambles()` to modify the related feature discovery logic

2. **Read the function's docstring and parameters** to confirm it handles your use case.

3. **Implement your changes** following the existing code style, error handling patterns, and naming conventions in the file.

4. **Test your changes:**
   ```bash
   pytest -k "preamble"
   ```

## Verify success

Your preamble integration works when:
- `get_preamble()` returns the expected string for valid features
- `get_related_preambles()` returns a list of related features with the correct structure
- All preamble tests pass without errors

## Key files

- `src/attune_author/preamble.py`
