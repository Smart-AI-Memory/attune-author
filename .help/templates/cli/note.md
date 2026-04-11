---
type: note
feature: cli
depth: note
generated_at: 2026-04-11T04:57:56.653037+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# Note: cli

## Context

The CLI provides the command-line interface for attune-author, supporting subcommands for bootstrap, generate, status, and maintain operations.

## Implementation

The CLI implementation centers on a single entry point function:

- `main(argv: list[str] | None = None) -> int` in `src/attune_author/cli.py`

You can call `main()` directly or use it as the console script entry point. The function accepts an optional argument list (defaulting to `sys.argv` when `None`) and returns an integer exit code following standard Unix conventions.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
