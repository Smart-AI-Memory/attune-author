---
type: note
feature: cli
depth: note
generated_at: 2026-04-14T14:10:05.707215+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Note: cli

## Context

The attune-author CLI provides subcommands for bootstrap, generate, status, and maintain operations through a single entry point.

## Content

The CLI module centers on the `main()` function in `src/attune_author/cli.py`, which serves as the primary entry point for all command-line operations. When you run attune-author from the command line, this function processes your arguments and routes them to the appropriate subcommand handlers.

The module displays "attune-author — documentation authoring for the attune ecosystem" as its welcome header when you invoke the CLI.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
