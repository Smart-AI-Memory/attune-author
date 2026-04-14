---
type: warning
feature: cli
depth: warning
generated_at: 2026-04-14T14:09:28.061010+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI cautions

## What to watch for

The CLI module provides the command-line interface for attune-author. While straightforward, there are specific areas where unexpected behavior can occur.

## Risk areas

**Exit code handling in `main()`**
The `main()` function returns an integer exit code, but the mapping between internal errors and exit codes may not be obvious. Different failure modes (invalid arguments, missing files, processing errors) should return distinct codes for proper shell integration.

**Argument parsing edge cases**
Command-line argument parsing can fail silently or produce unexpected results with malformed input, especially when dealing with file paths containing spaces or special characters.

**Standard stream handling**
Output formatting and error messages may behave differently when stdout/stderr are redirected or when running in non-interactive environments.

## How to avoid problems

1. **Test with realistic command lines.** Don't just test the happy path — try malformed arguments, missing files, and edge cases that real users might encounter:
   ```bash
   # Test these scenarios
   attune-author --nonexistent-flag
   attune-author generate ""
   attune-author bootstrap /path/with spaces/
   ```

2. **Verify exit codes explicitly.** When testing CLI functionality, check that the process exits with the expected code:
   ```python
   result = main(['generate', 'missing-file'])
   assert result != 0  # Should fail gracefully
   ```

3. **Test in different environments.** CLI behavior can vary between interactive shells, scripts, and CI environments. Test with redirected output and in non-TTY contexts.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
