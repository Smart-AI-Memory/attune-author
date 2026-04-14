---
type: troubleshooting
feature: preamble
depth: troubleshooting
generated_at: 2026-04-14T14:08:07.064954+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Troubleshoot preamble

## Before you start

The preamble feature provides context-sensitive one-liners for workflow skills based on project state and recent activity.

## Symptom table

| If you observe | Check |
|----------------|-------|
| `get_preamble()` returns `None` unexpectedly | Verify the feature name exists and help directory path is valid |
| Empty or wrong related preambles | Check if features share tags and `max_results` parameter |
| Exception during preamble lookup | Validate `feature_name` parameter and help directory structure |
| Preambles missing expected context | Confirm project state files and recent activity data are accessible |

## Step-by-step diagnosis

1. **Reproduce the failure in isolation.**
   Call `get_preamble()` or `get_related_preambles()` directly with minimal arguments to confirm the issue occurs outside your larger workflow. Use a known feature name first.

2. **Verify your inputs.**
   Check that your `feature_name` parameter matches an actual feature and that `help_dir` (if provided) points to a valid directory containing preamble data.

3. **Enable debug logging.**
   Set your logging level to `DEBUG` before calling preamble functions. The output will show which files are being read and what data is found.

4. **Inspect the entry points.**
   Add print statements or use a debugger in these key functions:
   - `get_preamble()` — Check if it finds the feature and processes the help directory correctly
   - `get_related_preambles()` — Verify tag matching logic and result limiting

5. **Run related tests.**
   Execute `pytest -k "preamble" -v` to see which preamble tests pass. Failed tests often reveal the same root cause as your issue.

## Common fixes

- **Missing help directory.** If `get_preamble()` returns `None`, ensure your help directory exists and contains the expected feature files. The function silently fails when it can't find preamble data.

- **Invalid feature name.** Check for typos in your `feature_name` parameter. The lookup is case-sensitive and must match exactly.

- **Corrupted preamble files.** If you get parsing errors, verify that preamble files in your help directory are properly formatted. Try regenerating them if they're auto-generated.

- **Outdated project state.** Related preambles depend on tag data that may be stale. Refresh your project metadata if context isn't reflecting recent changes.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
