---
type: concept
feature: cli
depth: concept
generated_at: 2026-04-14T14:09:00.172991+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI

The CLI module serves as the command-line entry point for attune-author, providing a unified interface for documentation authoring tasks in the attune ecosystem.

## Entry point structure

The module implements a single `main()` function that processes command-line arguments and coordinates the execution of various documentation operations. When you run attune-author from the command line, this function handles argument parsing and delegates to the appropriate subcommand handlers.

The welcome header identifies the tool as "attune-author — documentation authoring for the attune ecosystem", establishing the CLI's role in the broader attune toolchain.

## Command interface

The CLI supports multiple subcommands that cover the core documentation workflow:

- **bootstrap** — Initialize new documentation projects
- **generate** — Create documentation from source code
- **status** — Check the current state of documentation
- **maintain** — Perform ongoing maintenance tasks

Each subcommand encapsulates a specific aspect of the documentation authoring process, allowing you to perform targeted operations without running the entire toolchain.
