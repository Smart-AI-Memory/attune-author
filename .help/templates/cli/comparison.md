---
type: comparison
feature: cli
depth: comparison
generated_at: 2026-04-14T16:15:08.866367+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI vs programmatic API

## Context

The attune-author CLI provides a command-line interface for documentation authoring tasks including bootstrap, generate, status, and maintenance operations. You can choose between using the CLI commands or integrating attune-author functionality directly into your code.

## Feature comparison

| Aspect | CLI (`attune-author` command) | Programmatic API |
|--------|-------------------------------|------------------|
| **Setup** | Install once, use anywhere | Import modules in your code |
| **Automation** | Shell scripts, CI/CD pipelines | Python scripts, custom tooling |
| **Error handling** | Exit codes, stderr output | Python exceptions you can catch |
| **Configuration** | Command-line flags, config files | Direct parameter passing |
| **Interactive use** | Tab completion, help text | IDE integration, type hints |
| **Learning curve** | Familiar to command-line users | Requires Python knowledge |

## Use the CLI when...

- You want to run documentation tasks from the command line or shell scripts
- You're integrating with CI/CD systems that expect command-line tools
- You need a quick way to bootstrap, generate, check status, or maintain documentation
- Multiple team members need access without writing Python code
- You prefer the familiar pattern of `command --option value`

The CLI's `main()` function in `src/attune_author/cli.py` handles argument parsing and provides the standard command-line experience with proper exit codes.

## Use the programmatic API when...

- You're building custom tooling that needs fine-grained control over attune-author operations
- You want to embed documentation generation into a larger Python application
- You need to handle errors programmatically rather than relying on exit codes
- You're creating interactive tools that need to call attune-author functions conditionally
- You want type checking and IDE support for the parameters you pass

## Recommendation

**Start with the CLI** unless you specifically need programmatic integration. The command-line interface covers the most common workflows and provides better error messages for typical usage. Move to the programmatic API only when you need the flexibility to handle results in Python code or integrate deeply with custom tooling.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
