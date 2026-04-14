---
type: error
feature: cli
depth: error
generated_at: 2026-04-14T16:14:15.559846+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI errors

Command-line interface failures occur when the attune-author CLI entry point encounters invalid arguments, missing dependencies, or runtime errors during command execution.

## Common error signatures

- `SystemExit` with non-zero exit codes from argument parsing failures
- `ModuleNotFoundError` when CLI dependencies are not installed
- `FileNotFoundError` when CLI attempts to access missing configuration or input files
- `PermissionError` when CLI lacks write access to output directories
- Return codes from `main()` function indicating command failures

## Where errors originate

CLI errors stem from the main entry point:

- `main()` in `src/attune_author/cli.py` — Processes command-line arguments and orchestrates subcommand execution

## How to diagnose

1. **Check the exit code.** Non-zero return values from `main()` indicate the type of failure: argument validation, missing files, or subcommand execution errors.

2. **Run with `--help` to verify syntax.** Invalid subcommands or missing required arguments trigger immediate failures with usage information.

3. **Verify file permissions and paths.** Many CLI errors occur when the tool cannot read input files or write to the specified output location.

4. **Test with minimal arguments.** Strip down to the simplest valid command to isolate whether the issue is with argument parsing or the underlying functionality.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
