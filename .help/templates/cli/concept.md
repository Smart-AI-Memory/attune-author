---
type: concept
feature: cli
depth: concept
generated_at: 2026-04-14T16:13:57.456552+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Cli

## How it works

The CLI module provides the command-line interface for attune-author, serving as the primary entry point for documentation authoring tasks in the attune ecosystem.

When you run `attune-author` from the command line, the `main()` function processes your command-line arguments and routes them to the appropriate functionality. The interface displays "attune-author — documentation authoring for the attune ecosystem" as its welcome header, establishing the tool's purpose and scope.

## Entry point

The `main()` function accepts an optional list of command-line arguments and returns an integer exit code. If you don't provide arguments, it reads them from `sys.argv`. This design allows the CLI to work both as a standalone command-line tool and as a programmatically callable interface for testing or integration purposes.
