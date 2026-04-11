---
type: faq
feature: cli
depth: faq
generated_at: 2026-04-11T04:57:39.304855+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# CLI FAQ

## What is the CLI?

The command-line interface for attune-author. It provides subcommands for bootstrap, generate, status, and maintain operations.

## When should I use the CLI?

Use the CLI when you need to run attune-author from the command line or integrate it into scripts and automation workflows.

## How do I run attune-author from the command line?

Call the `main()` function in `src/attune_author/cli.py`, which serves as the CLI entry point. This function processes command-line arguments and executes the appropriate subcommand.

## How do I debug CLI issues?

First, run the CLI-related tests with `pytest -k "cli" -v`. If the tests pass but you're still experiencing problems, add a `logger.debug` statement at the suspected failure point and re-run with logging enabled to see detailed execution information.

## Where is the CLI code located?

The CLI implementation is in `src/attune_author/cli.py`.

**Tags:** `cli`, `commands`, `entrypoint`
