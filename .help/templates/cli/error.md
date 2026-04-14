---
type: error
feature: cli
depth: error
generated_at: 2026-04-14T14:09:19.461049+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI errors

CLI errors occur when the attune-author command-line interface fails to parse arguments, execute subcommands, or handle exit conditions properly.

## Common error signatures

Since the CLI module contains only the main entry point function, specific exception types depend on the subcommands and argument parsing implementation:

- **Argument parsing failures** — Invalid command syntax or unrecognized options
- **Subcommand execution failures** — Errors from bootstrap, generate, status, or maintain operations
- **Exit code handling** — Non-zero return values indicating command failure

## Where errors originate

CLI errors originate from the main entry point:

- `main()` in `src/attune_author/cli.py` — Processes command-line arguments and delegates to subcommands

## How to diagnose

1. **Run the failing command with verbose output.** Add `-v` or `--verbose` flags if available to see detailed operation logs.

2. **Check the exit code.** The `main()` function returns an integer — zero indicates success, non-zero values indicate specific failure modes.

3. **Verify command syntax.** Ensure you're using valid subcommands (bootstrap, generate, status, maintain) and that all required arguments are provided.

4. **Test with minimal arguments.** Start with the simplest valid command form and add complexity incrementally to isolate where parsing or execution fails.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
