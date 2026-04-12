---
type: concept
feature: cli
depth: concept
generated_at: 2026-04-12T04:53:33.991615+00:00
source_hash: b40b5cd02e5e4ea8d4a6bf7a3a528cdf03aee2a0e01db1dbdc1a9be426d9af1f
status: generated
---

# CLI

The CLI is the command-line interface that provides the primary entry point for attune-author operations.

## Entry point architecture

The `main()` function serves as the single entry point for all command-line interactions with attune-author. When you run the attune-author command, this function processes the command-line arguments and routes them to the appropriate subcommands for bootstrap, generate, status, and maintain operations.

## Interface structure

| Function | Purpose | Location |
|----------|---------|----------|
| `main()` | Processes command-line arguments and executes the requested operation | `src/attune_author/cli.py` |

The function accepts an optional `argv` parameter, allowing it to process either system command-line arguments or custom argument lists for testing and programmatic use.
