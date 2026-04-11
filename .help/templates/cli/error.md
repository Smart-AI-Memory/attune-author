---
type: error
feature: cli
depth: error
generated_at: 2026-04-11T04:57:08.896876+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# CLI errors

Command-line interface failures that occur when running attune-author commands or parsing arguments.

## Common error signatures

- `SystemExit` — Command failed or invalid arguments provided
- `argparse.ArgumentError` — Invalid command-line arguments or missing required parameters
- Exit codes 1-2 — Standard CLI error returns from the main entry point

## Where errors originate

CLI errors originate from the main entry point that handles command parsing and execution:

- `main()` in `src/attune_author/cli.py` — Processes command-line arguments and dispatches to subcommands (bootstrap, generate, status, maintain)

## How to diagnose

1. **Check the exit code.** The `main()` function returns specific exit codes that indicate the type of failure. A non-zero exit code means the command encountered an error.

2. **Examine the command arguments.** Most CLI errors stem from invalid arguments, missing required parameters, or incorrect subcommand usage. Verify the command syntax against the help output.

3. **Run with help flags.** Use `--help` or `-h` to see available commands and required arguments. Each subcommand (bootstrap, generate, status, maintain) has its own argument requirements.

4. **Check file permissions and paths.** Since attune-author operates on files and directories, verify that specified paths exist and are accessible with appropriate read/write permissions.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
