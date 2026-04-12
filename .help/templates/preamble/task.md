---
type: task
feature: preamble
depth: task
generated_at: 2026-04-12T04:19:55.900394+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Work with preamble

Use preamble when you need to display contextual one-liner descriptions for workflow features or find related features based on shared functionality tags.

## Prerequisites

- Access to the project source code
- Familiarity with the files under src/attune_author/preamble.py

## Identify the target function

1. **Determine your goal:**
   - To retrieve a single feature's description: use `get_preamble()`
   - To find related features by tags: use `get_related_preambles()`

2. **Locate the function in `src/attune_author/preamble.py`:**
   - `get_preamble(feature_name, help_dir)` — Returns the one-liner description for a specific feature
   - `get_related_preambles(feature_name, help_dir, max_results)` — Returns up to 3 features with shared tags

## Modify preamble behavior

1. **Read the function's docstring and parameters** to confirm it handles your use case.

2. **Update the function logic** following the existing code style:
   - Use the same naming conventions as surrounding functions
   - Handle errors consistently with the existing error patterns
   - Add logging statements that match the current format

3. **Test your changes** by running:
   ```bash
   pytest -k "preamble"
   ```

## Verify success

Your changes work correctly when the preamble tests pass and your target function returns the expected preamble text or related feature list based on your modifications.

## Key files

- `src/attune_author/preamble.py`
