---
type: comparison
feature: cli
depth: comparison
generated_at: 2026-04-11T04:58:00.898222+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# CLI vs programmatic interface

## Context

The attune-author CLI provides a command-line interface with subcommands for bootstrap, generate, status, and maintain operations. You can either use these commands from your terminal or call the underlying functions directly in your Python code.

## CLI vs programmatic access

| Aspect | CLI commands | Direct function calls |
|--------|-------------|----------------------|
| **Setup** | Zero imports, works from any directory | Requires Python imports and module setup |
| **Error handling** | Returns exit codes, prints user-friendly messages | Raises exceptions you must catch |
| **Integration** | Easy to call from shell scripts and CI/CD | Natural fit for Python applications |
| **Debugging** | Limited to CLI output and exit codes | Full access to Python debugging tools |
| **Batch operations** | Requires shell scripting for multiple targets | Can loop and process results in memory |

## Use the CLI when

- You're working interactively in a terminal
- You need to integrate with shell scripts or CI/CD pipelines
- You want the tool to handle error formatting and exit codes
- You're performing one-off operations like bootstrapping a new project

The main entry point is `main()` in `src/attune_author/cli.py`, which provides the standard command-line interface with proper argument parsing and error handling.

## Use programmatic access when

- You're building a Python application that needs to embed attune-author functionality
- You need fine-grained control over error handling and recovery
- You want to process results in memory rather than parsing CLI output
- You're writing tests that need to verify specific function behavior

## Limitations

The CLI interface:
- Cannot expose every parameter that underlying functions accept
- Adds overhead for simple operations that don't need argument parsing
- Requires subprocess calls if you're already running Python code

For exploratory work or one-time scripts, consider using the underlying functions directly rather than wrapping CLI calls in Python.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
