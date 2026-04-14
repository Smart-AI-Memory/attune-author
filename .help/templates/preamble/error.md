---
type: error
feature: preamble
depth: error
generated_at: 2026-04-14T14:07:44.212063+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble errors

Preamble failures occur when the system cannot retrieve or process context-sensitive preambles for workflow skills.

## Common error signatures

- `FileNotFoundError` when help directory paths don't exist or aren't accessible
- `ValueError` when feature names are empty, invalid, or contain unexpected characters
- `TypeError` when help_dir parameter receives incompatible types
- JSON parsing errors when preamble metadata files are malformed

## Where errors originate

Preamble errors typically emerge from these two functions:

- `get_preamble()` — Fails when retrieving individual feature preambles due to missing files or invalid feature names
- `get_related_preambles()` — Fails when searching for related features, often due to corrupted tag metadata or filesystem access issues

## How to diagnose

1. **Verify the feature name exists.** Check that the feature name you're requesting actually has a corresponding preamble file in the help directory structure.

2. **Confirm help directory accessibility.** Ensure the help_dir path exists and your process has read permissions. If help_dir is None, verify the default help directory is properly configured.

3. **Validate preamble file format.** If get_preamble() returns None unexpectedly, inspect the target preamble file for syntax errors or missing required metadata fields.

4. **Check tag consistency for related preambles.** When get_related_preambles() fails or returns empty results, examine whether the source feature and potential matches share valid tag metadata.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
