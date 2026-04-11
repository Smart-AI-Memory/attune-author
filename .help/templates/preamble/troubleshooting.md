---
type: troubleshooting
feature: preamble
depth: troubleshooting
generated_at: 2026-04-11T04:56:02.737358+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50d133b0
status: generated
---

# Troubleshoot preamble

## Before you start

The preamble feature provides context-sensitive one-liners for workflow skills based on feature names and related content tags.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `get_preamble()` returns `None` | Verify the feature name exists in your help directory |
| Empty list from `get_related_preambles()` | Check that features have shared tags in their metadata |
| `FileNotFoundError` or path errors | Confirm the `help_dir` parameter points to a valid directory |
| Wrong preamble returned | Inspect the feature's metadata file for correct content |

## Step-by-step diagnosis

1. **Reproduce with minimal inputs.**
   Test the failing function call with just the required `feature_name` parameter:
   ```python
   from attune_author.preamble import get_preamble
   result = get_preamble("your_feature_name")
   ```

2. **Verify the help directory structure.**
   Check that your help directory contains the expected feature files:
   ```bash
   ls -la your_help_dir/
   # Look for feature directories or metadata files
   ```

3. **Test with explicit help_dir path.**
   If you're relying on the default `help_dir`, try specifying it explicitly:
   ```python
   get_preamble("feature_name", help_dir="/path/to/your/help")
   ```

4. **Examine function behavior directly.**
   Add debug prints to see what the functions actually receive and return:
   - `get_preamble()` should return a string or None
   - `get_related_preambles()` should return a list of dictionaries

## Common fixes

- **Missing feature metadata.** Create or repair the metadata file for your feature in the help directory.

- **Invalid help directory path.** Set the `help_dir` parameter to the correct path, or ensure your default help directory is properly configured.

- **Feature name mismatch.** Use the exact feature name as it appears in your help directory structure (case-sensitive).

- **Missing or malformed tags.** For `get_related_preambles()` to work, features need shared tags in their metadata. Add appropriate tags to feature files.

- **Path resolution issues.** Convert string paths to `Path` objects if you're passing complex path structures:
   ```python
   from pathlib import Path
   get_preamble("feature", help_dir=Path("/absolute/path"))
   ```

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
