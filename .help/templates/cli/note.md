---
type: note
feature: cli
depth: note
generated_at: 2026-04-14T16:15:04.466559+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Note: cli

## Context

The CLI module provides the command-line interface for attune-author, displaying the welcome message "attune-author — documentation authoring for the attune ecosystem" when invoked.

## Entry point

The `main()` function in `src/attune_author/cli.py` serves as the primary entry point for the command-line interface. You can call it directly with an optional argument list, and it returns an integer exit code following standard CLI conventions.

The module follows a function-first design — you call `main()` directly without creating any class instances.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
