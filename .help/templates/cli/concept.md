---
type: concept
feature: cli
depth: concept
generated_at: 2026-04-26T19:48:32.149684+00:00
source_hash: f0f928daa13f792e7874da74f9fd669dc0e772acc208349a075625078eeb59c7
status: generated
---

# Cli

The CLI is the command-line interface for attune-author, providing access to documentation authoring commands through a single entry point.

## How it works

The CLI acts as the user-facing gateway to attune-author functionality. When you run `attune-author` in your terminal, it routes to the `main()` function in the cli module, which presents the welcome header "attune-author — documentation authoring for the attune ecosystem" and handles command parsing and execution.

The system follows a standard CLI pattern where `main()` accepts an optional argument list (defaulting to command-line arguments) and returns an integer exit code to indicate success or failure to the shell.

## Entry point structure

The CLI provides a single point of access:

- **`main(argv)`** — Processes command-line arguments and coordinates subcommand execution

The function signature `main(argv: list[str] | None = None) -> int` allows the CLI to work both as a standalone command-line tool and as a programmatically callable interface for testing or integration scenarios.

## Integration points

Other parts of the attune-author system interact with the CLI through:

| Function | Purpose | Location |
|----------|---------|----------|
| `main()` | CLI entry point and command router | `src/attune_author/cli.py` |

The CLI serves as the primary interface between users and the attune-author documentation system, translating command-line intentions into internal function calls.
