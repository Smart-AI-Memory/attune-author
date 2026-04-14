---
type: warning
feature: preamble
depth: warning
generated_at: 2026-04-14T14:07:53.089945+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Preamble cautions

## What to watch for

The preamble system renders context-sensitive descriptions for workflow skills, but its file-based lookups can fail silently in ways that break the user experience.

## Risk areas

**Missing preamble files cause silent degradation.** When `get_preamble()` can't find a matching file for a feature, it returns `None` instead of raising an error. This means workflows continue running but users see empty or broken context descriptions. The failure often goes unnoticed until someone manually tests the affected feature.

**Related preamble searches may return stale results.** `get_related_preambles()` uses tag-based matching to find similar features, but it doesn't validate that the returned preambles are current or that their source files still exist. If you rename or move feature files without updating the tag system, users get outdated suggestions.

**Help directory resolution depends on runtime context.** Both functions use an optional `help_dir` parameter that defaults to autodiscovery. In development environments or non-standard deployments, the autodiscovery may point to the wrong directory or fail entirely, causing all preamble lookups to return empty results.

## How to avoid problems

1. **Validate preamble files exist before deployment.** Add a test that verifies every feature referenced in your workflow has a corresponding preamble file. This catches missing files before they reach production.

2. **Set help directory explicitly in production code.** Rather than relying on autodiscovery, pass a known-good `help_dir` path when calling preamble functions in production workflows. This eliminates environment-dependent failures.

3. **Monitor for None returns.** When `get_preamble()` returns `None`, log the feature name and help directory path. This gives you visibility into which lookups are failing and why.

4. **Limit related preamble results.** The `max_results` parameter defaults to 3, but returning fewer results (1-2) reduces the chance of showing stale suggestions to users.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
