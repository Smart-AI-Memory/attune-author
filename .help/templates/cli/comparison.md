---
type: comparison
feature: cli
depth: comparison
generated_at: 2026-04-14T14:10:09.981441+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI vs programmatic API

## Context

The `attune-author` package provides two ways to access its functionality: through the command-line interface or by importing and calling functions directly in your Python code.

## Feature comparison

| Aspect | CLI | Programmatic API |
|--------|-----|------------------|
| **Access method** | Terminal commands | Python imports |
| **Target users** | Content authors, build scripts | Developers, automation |
| **Error handling** | Exit codes, terminal output | Exceptions you can catch |
| **Integration** | Shell scripts, CI/CD pipelines | Python applications |
| **Learning curve** | Minimal - standard command patterns | Requires Python knowledge |
| **Flexibility** | Fixed subcommands only | Full control over function calls |

## Use CLI when...

- You're authoring documentation and want the fastest path to common tasks
- You're writing shell scripts or configuring CI/CD pipelines
- You prefer terminal workflows over Python programming
- You need the bootstrap, generate, status, or maintain subcommands exactly as designed
- You want consistent behavior across different environments

The CLI entry point (`main()` in `src/attune_author/cli.py`) handles argument parsing, error reporting, and exit codes automatically.

## Use the programmatic API when...

- You're building a larger Python application that needs documentation generation
- You need custom error handling or want to catch specific exceptions
- You want to compose attune-author functions with other Python libraries
- You need behavior that the CLI subcommands don't expose
- You're writing tests that need fine-grained control over inputs and outputs

## Recommendation

**Start with the CLI** unless you're already writing Python code. The command-line interface covers the most common documentation authoring workflows and requires no programming knowledge. Switch to the programmatic API only when you hit specific limitations or need to integrate attune-author into a larger Python application.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
