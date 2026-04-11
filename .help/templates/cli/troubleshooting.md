---
type: troubleshooting
feature: cli
depth: troubleshooting
generated_at: 2026-04-11T04:57:28.314992+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# Troubleshoot cli

## Before you start

The CLI entry point provides command-line access to attune-author with subcommands for bootstrap, generate, status, and maintain.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Unexpected exception | Python's traceback for the exact file and line where the error occurs |
| Silent failure / wrong result | Return values from `main()` and any early exit conditions |
| Intermittent behavior | Environment variables, global state, or cached data between runs |
| Slow execution | I/O operations, loops, and calls to external processes or subsystems |

## Step-by-step diagnosis

1. **Reproduce the failure in isolation.**
   Create a minimal test case with only the required arguments. Run the CLI command directly to confirm the issue occurs outside any wrapper scripts or IDE integrations.

2. **Enable verbose logging.**
   Set logging to `DEBUG` level and re-run the command. Check both stdout and stderr for error messages or unexpected behavior patterns.

3. **Inspect the main entry point.**
   Examine the `main()` function in `src/attune_author/cli.py`. Look for:
   - Argument parsing errors
   - Missing subcommand handlers
   - Exception handling that might swallow errors

4. **Check related tests.**
   Run `pytest -k "cli" -v` to see which CLI tests pass or fail. Use passing test fixtures as a reference for correct usage patterns.

## Common fixes

- **Fix argument parsing errors.** Verify that command-line arguments match expected formats. Use `--help` to confirm available options and required parameters.

- **Clear environment state.** Remove any cached files, temporary directories, or environment variables that might interfere:
  ```bash
  unset ATTUNE_*
  rm -rf ~/.cache/attune-author/
  ```

- **Update dependencies.** Check for version conflicts that affect CLI behavior:
  ```bash
  pip show click argparse
  pip install --upgrade attune-author
  ```

- **Validate subcommand availability.** Ensure the specific subcommand (bootstrap, generate, status, maintain) is properly registered and accessible.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
