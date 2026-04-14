---
type: task
feature: preamble
depth: task
generated_at: 2026-04-14T14:07:30.302873+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Work with preamble

Use preamble when you need to display contextual one-liner descriptions for workflow features or discover related functionality through shared tags.

## Prerequisites

- Access to the project source code
- Python development environment set up

## Review existing functionality

1. **Examine the preamble module structure.**
   Open `src/attune_author/preamble.py` and review the two main functions:
   - `get_preamble()` — retrieves a single feature's descriptive one-liner
   - `get_related_preambles()` — finds up to 3 related features by shared tags

2. **Test current behavior.**
   Run a few calls to see the existing output format and determine what changes you need.

## Modify preamble behavior

1. **Choose the appropriate function.**
   - Modify `get_preamble()` if you need to change how individual feature descriptions are retrieved or formatted
   - Modify `get_related_preambles()` if you need to adjust the relationship discovery logic or result limits

2. **Implement your changes.**
   Follow the existing error handling patterns and maintain the same return types: `str | None` for single preambles, `list[dict[str, str]]` for related preambles.

3. **Verify your changes work.**
   Run `pytest -k "preamble"` to ensure your modifications don't break existing functionality.

## Verify success

Your changes work correctly when:
- `get_preamble()` returns the expected string format for valid feature names
- `get_related_preambles()` returns a list of dictionaries with the correct structure
- All preamble tests pass without errors

## Key files

- `src/attune_author/preamble.py`
