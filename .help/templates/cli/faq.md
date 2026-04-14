---
type: faq
feature: cli
depth: faq
generated_at: 2026-04-14T16:14:47.131369+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI FAQ

## What is the CLI module?

The CLI module provides the command-line entry point for attune-author, giving you access to subcommands for bootstrap, generate, status, and maintain operations.

## When should I use the CLI?

Use the CLI when you want to run attune-author from the command line rather than importing it as a library. The CLI gives you access to all core functionality through simple commands.

## How do I run attune-author from the command line?

Call the `main()` function in `src/attune_author/cli.py`. This function serves as the CLI entry point and handles command parsing and execution.

## How do I debug CLI issues?

First, run the CLI-related tests with `pytest -k "cli" -v`. If the tests pass but you're still having problems, add `logger.debug` statements where you suspect the issue occurs and re-run with logging enabled.

## Where are the CLI source files?

The CLI implementation is in `src/attune_author/cli.py`.

**Tags:** `cli`, `commands`, `entrypoint`
