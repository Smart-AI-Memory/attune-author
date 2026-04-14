---
type: faq
feature: cli
depth: faq
generated_at: 2026-04-14T14:09:50.501132+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI FAQ

## What is the CLI?

The command-line interface for attune-author. It provides subcommands for bootstrap, generate, status, and maintain operations.

## When should I use the CLI?

Use the CLI when you need to run attune-author commands from the terminal. This is the primary way to interact with attune-author's documentation authoring tools.

## How do I run attune-author commands?

Call the `main()` function in `src/attune_author/cli.py`, which serves as the CLI entry point. This function handles command-line arguments and routes them to the appropriate subcommands.

## How do I debug CLI issues?

Run the related tests first: `pytest -k "cli" -v`. If they pass but your code still fails, add a `logger.debug` statement at the suspected failure point and re-run with logging enabled.

For common failure modes, see the troubleshooting page for this feature.

## Where are the source files?

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
