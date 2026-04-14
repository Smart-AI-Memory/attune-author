---
type: task
feature: preamble
depth: task
generated_at: 2026-04-14T16:12:26.441863+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Work with preamble

Use preamble when you need to display context-sensitive help text that guides users based on their current project state and recent activity.

## Prerequisites

- Access to the project source code
- Understanding of the preamble module at `src/attune_author/preamble.py`

## Retrieve a feature's preamble

1. **Import the preamble module.**
   ```python
   from attune_author.preamble import get_preamble
   ```

2. **Call get_preamble with the feature name.**
   ```python
   preamble_text = get_preamble("your_feature_name")
   ```

3. **Handle the result.**
   The function returns a string if the preamble exists, or `None` if no preamble is found for the feature.

## Find related preambles

1. **Import the related preambles function.**
   ```python
   from attune_author.preamble import get_related_preambles
   ```

2. **Retrieve related preambles.**
   ```python
   related = get_related_preambles("your_feature_name", max_results=3)
   ```

3. **Process the results.**
   The function returns a list of dictionaries, each containing feature names and their preamble text for features that share tags with your target feature.

## Modify preamble behavior

1. **Locate the function you need to change.**
   - Use `get_preamble()` to change how individual feature preambles are retrieved
   - Use `get_related_preambles()` to modify the logic for finding related features

2. **Read the function's docstring and parameters.**
   Confirm the function handles your specific use case before modifying its implementation.

3. **Update the function code.**
   Maintain the existing parameter types and return format to avoid breaking dependent code.

4. **Test your changes.**
   Run `pytest -k "preamble"` to verify your modifications work correctly and don't introduce regressions.

## Verify success

Your preamble integration works when:
- `get_preamble()` returns the expected string for valid feature names
- `get_related_preambles()` returns a list of related features with their preamble text
- All existing tests continue to pass after your modifications

## Key files

- `src/attune_author/preamble.py` — Main preamble functionality
