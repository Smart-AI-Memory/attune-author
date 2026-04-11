---
type: concept
feature: cli
depth: concept
generated_at: 2026-04-11T04:56:52.006728+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# CLI

The CLI module provides the command-line interface for attune-author, serving as the primary entry point for users to interact with the tool's functionality.

## Command structure

The CLI organizes attune-author's capabilities into subcommands that handle different aspects of the authoring workflow:

- **bootstrap** — Set up initial project structure
- **generate** — Create content from templates
- **status** — Check project state
- **maintain** — Perform ongoing project maintenance

## Entry point

The `main()` function serves as the single entry point for all command-line operations. When you run attune-author from the command line, this function processes the arguments and routes them to the appropriate subcommand handler.

| Function | Purpose | Location |
|----------|---------|----------|
| `main()` | Processes command-line arguments and executes subcommands | `src/attune_author/cli.py` |
