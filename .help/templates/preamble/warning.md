---
type: warning
feature: preamble
depth: warning
generated_at: 2026-04-11T04:55:48.787758+00:00
source_hash: 3e02ceee37af71750f50dd40ecd95359ea5c4aaf1a1a7e50691cfb6250d133b0
status: generated
---

# Preamble cautions

## What to watch for

The preamble system renders context-sensitive one-liners for workflow skills, but it fails silently when feature names don't match and can return unexpected results when help directories are misconfigured.

## Risk areas

### Missing feature names return None without error

`get_preamble()` returns `None` when the feature name doesn't exist in the help system. This silent failure can leave your workflow skills without context, making them harder for users to understand. Always check the return value or have a fallback message ready.

### Help directory paths affect preamble lookup

Both `get_preamble()` and `get_related_preambles()` accept an optional `help_dir` parameter. When you pass `None` (the default), the functions use a default help directory. If this default doesn't match your project structure, preambles won't load. Explicitly set the help directory when working with non-standard project layouts.

### Related preambles can return fewer than expected results

`get_related_preambles()` limits results to 3 by default via the `max_results` parameter. When features share multiple tags, you might expect more related items but only get the first few matches. The function also returns empty lists when no related features exist, rather than falling back to similar alternatives.

## How to avoid problems

1. **Validate feature names before lookup.** Check that the feature exists in your help system before calling `get_preamble()`. Consider maintaining a list of valid feature names or implementing a feature existence check.

2. **Set explicit help directory paths.** Don't rely on default help directory behavior. Pass an explicit `help_dir` parameter that matches your project's documentation structure.

3. **Handle None returns gracefully.** Always provide fallback text when `get_preamble()` returns `None`:
   ```python
   preamble = get_preamble(feature_name) or "General workflow assistance"
   ```

4. **Test with your actual help directory structure.** Preamble lookup depends on your help files being organized correctly. Test with your real directory structure, not just mock data.

## Source files

- `src/attune_author/preamble.py`

**Tags:** `context`, `rendering`, `workflow`
