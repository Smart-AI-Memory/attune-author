---
type: troubleshooting
feature: preamble
depth: troubleshooting
generated_at: 2026-04-14T16:13:04.469463+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Troubleshoot preamble

## Before you start

The preamble feature provides context-sensitive one-liners for workflow skills based on project state and recent activity.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `get_preamble()` returns `None` unexpectedly | Verify the feature name exists in your help directory and matches exactly |
| Related preambles missing or incomplete | Check if features share tags and that tag files are present in the help system |
| Function raises `FileNotFoundError` | Confirm the help directory path exists and contains the expected feature files |
| Wrong preamble content returned | Validate the feature name spelling and check for cached/stale content |

## Step-by-step diagnosis

1. **Reproduce with minimal input.**
   Test the failing function directly with only the required `feature_name` parameter:
   ```python
   from attune_author.preamble import get_preamble
   result = get_preamble("your_feature_name")
   print(f"Result: {result}")
   ```

2. **Verify feature existence.**
   Check that your feature name corresponds to an actual help file:
   ```bash
   find /path/to/help/dir -name "*your_feature_name*"
   ```

3. **Test with explicit help directory.**
   If using the default help directory fails, specify the path explicitly:
   ```python
   result = get_preamble("feature_name", help_dir="/path/to/your/help")
   ```

4. **Check related preambles separately.**
   Test `get_related_preambles()` to isolate tag-based lookup issues:
   ```python
   from attune_author.preamble import get_related_preambles
   related = get_related_preambles("feature_name", max_results=1)
   print(f"Found {len(related)} related features")
   ```

## Common fixes

- **Fix feature name typos.** Use exact case-sensitive names that match your help files. Run `ls` in your help directory to confirm available features.

- **Set correct help directory path.** If you're not using the default location, pass the `help_dir` parameter:
  ```python
  get_preamble("feature", help_dir="/custom/path/to/help")
  ```

- **Verify help file structure.** Ensure your help directory contains the expected metadata and tag files that the preamble system depends on.

- **Clear any file system caches.** If you recently added or modified help files, restart your Python process to clear any cached file handles or directory listings.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
