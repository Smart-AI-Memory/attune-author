---
type: error
feature: preamble
depth: error
generated_at: 2026-04-14T16:12:40.683286+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble errors

Failures when retrieving context-sensitive preambles for workflow skills, typically related to missing files, invalid feature names, or filesystem access issues.

## Common error signatures

- `FileNotFoundError` — Help directory or preamble files don't exist at the specified path
- `ValueError` — Invalid feature name parameter passed to preamble functions
- `PermissionError` — Insufficient permissions to read help directory or preamble files
- `KeyError` — Feature name not found in available preambles
- `TypeError` — Incorrect parameter types passed to `get_preamble()` or `get_related_preambles()`

## Where errors originate

Preamble errors occur in two main functions:

- `get_preamble()` — Retrieves single feature preambles; fails when the feature name is invalid or help files are inaccessible
- `get_related_preambles()` — Finds related features by shared tags; fails when tag matching or result limiting encounters invalid data

Both functions read from the help directory, so filesystem issues affect all preamble operations.

## How to diagnose

1. **Verify the help directory exists.** Check that the `help_dir` parameter points to a valid directory containing preamble files. If `help_dir` is None, the functions use a default location that may not exist.

2. **Confirm the feature name is valid.** Ensure the `feature_name` parameter matches an actual feature with available preamble content. Invalid feature names cause lookup failures.

3. **Check file permissions.** Verify that your process has read access to the help directory and its contents. Permission errors prevent preamble file access.

4. **Test with known working features.** Try calling `get_preamble()` with a feature name you know exists to isolate whether the issue is with the specific feature or the preamble system itself.

5. **Validate the max_results parameter.** For `get_related_preambles()`, ensure `max_results` is a positive integer. Invalid values cause parameter validation failures.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
