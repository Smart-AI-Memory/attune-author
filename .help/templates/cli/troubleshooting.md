---
type: troubleshooting
feature: cli
depth: troubleshooting
generated_at: 2026-04-14T16:14:34.042864+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Troubleshoot cli

## Before you start

The cli module provides the command-line entry point for attune-author. When you run `attune-author` commands, they flow through the `main()` function in this module, which displays the welcome header and routes to appropriate subcommands.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Command not found error | Verify `attune-author` is installed and in your PATH |
| Python traceback on startup | Check the `main()` function arguments and return handling |
| Wrong command output | Confirm you're using the correct subcommand syntax |
| Command hangs or runs slowly | Look for blocking I/O or infinite loops in argument parsing |

## Step-by-step diagnosis

1. **Test the basic entry point.**
   Run `attune-author --help` or `python -m attune_author.cli` to confirm the module loads and the welcome header displays correctly.

2. **Isolate the failing command.**
   Strip your command down to its minimal form. If `attune-author generate --complex-options` fails, try just `attune-author generate` first.

3. **Check the argument parsing.**
   Add debug prints or use a debugger in the `main()` function to inspect what arguments are being passed in the `argv` parameter.

4. **Enable Python's verbose mode.**
   Run with `python -v -m attune_author.cli` to see module loading issues, or add `print()` statements in `main()` to trace execution flow.

## Common fixes

- **Reinstall the package.** If the command isn't found, reinstall with `pip install -e .` from the project root to ensure the console script entry point is properly registered.

- **Check your Python environment.** Confirm you're running in the correct virtual environment with `which python` and `pip list | grep attune-author`.

- **Validate command syntax.** The cli module expects specific subcommands. Run `attune-author --help` to see available options and confirm your syntax matches.

- **Clear Python cache.** Remove `__pycache__` directories with `find . -name "__pycache__" -type d -exec rm -rf {} +` if you're seeing import errors after code changes.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
