---
type: error
feature: preamble
depth: error
generated_at: 2026-04-11T04:55:40.514056+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Preamble errors

Failures in retrieving context-sensitive preambles for workflow features, typically due to missing help files or invalid feature names.

## Common error signatures

- `FileNotFoundError` when the help directory path doesn't exist
- `KeyError` when requesting preambles for non-existent features
- `PermissionError` when the help directory is not readable
- `ValueError` when feature names contain invalid characters or formatting

## Where errors originate

- `get_preamble()` in `src/attune_author/preamble.py` — Fails when feature help files are missing or the help directory is inaccessible
- `get_related_preambles()` in `src/attune_author/preamble.py` — Errors when tag parsing fails or when the maximum results count is invalid

## How to diagnose

1. **Verify the help directory exists.** Check that the `help_dir` parameter points to a valid, readable directory containing feature documentation files.

2. **Confirm the feature name is valid.** Ensure the `feature_name` parameter matches an existing feature with available help documentation.

3. **Check file permissions.** Verify that your process has read access to both the help directory and its contained files.

4. **Validate the max_results parameter.** For `get_related_preambles()`, confirm that `max_results` is a positive integer.

5. **Examine the help file format.** Ensure that feature help files contain properly formatted preamble content and tag metadata.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
