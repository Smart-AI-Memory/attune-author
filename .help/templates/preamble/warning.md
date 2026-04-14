---
type: warning
feature: preamble
depth: warning
generated_at: 2026-04-14T16:12:52.668906+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble cautions

## What to watch for

The preamble module generates context-sensitive introductions for workflow skills, but several aspects of its behavior can catch you off guard during development.

## Risk areas

**Missing help directories cause silent failures**
`get_preamble()` returns `None` when it can't find the specified help directory, rather than raising an exception. This can lead to workflows displaying empty preambles without any indication that the lookup failed.

**Related preambles may return fewer results than expected**
`get_related_preambles()` uses tag matching to find related features, but if your feature has unique tags or the help directory structure changes, you might get an empty list even when related features exist. The function doesn't distinguish between "no matches found" and "lookup failed."

**Feature name matching is case-sensitive**
Both functions expect exact feature name matches. A typo or inconsistent casing in the `feature_name` parameter will result in no results, but the functions won't indicate whether the failure was due to a missing feature or an incorrect name.

## How to avoid problems

1. **Validate help directory paths before calling preamble functions.** Check that the directory exists and contains the expected structure before passing it to `get_preamble()` or `get_related_preambles()`.

2. **Handle None returns explicitly.** Always check if `get_preamble()` returns `None` and have a fallback strategy, such as using a default preamble or logging the missing feature for debugging.

3. **Verify feature names in your test data.** Create a test that confirms your feature names match what's actually in the help directory structure, especially after refactoring or renaming operations.

4. **Test with realistic help directory structures.** Don't just test with minimal fixtures — use a copy of your actual help directory to catch tag matching and feature discovery issues.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
