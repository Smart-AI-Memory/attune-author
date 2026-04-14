---
type: warning
feature: cli
depth: warning
generated_at: 2026-04-14T16:14:24.154382+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# CLI cautions

## What to watch for

The CLI module serves as the command-line entry point for attune-author, handling argument parsing and dispatching to subcommands like bootstrap, generate, status, and maintain.

## Risk areas

**Exit code handling in production scripts**
The `main()` function returns integer exit codes, but these can be lost if you call it from Python code that doesn't check the return value. Scripts that wrap the CLI may appear to succeed even when the underlying command fails.

**Command-line argument injection**
If you pass user input directly to `main(argv=...)`, malicious arguments could trigger unintended behavior. This is particularly risky when building wrapper scripts or web interfaces that invoke CLI commands.

**Environment-dependent behavior**
The CLI may behave differently based on the current working directory, environment variables, or installed dependencies. Commands that work in development may fail in deployment environments with different configurations.

## How to avoid problems

1. **Always check exit codes.** When calling `main()` programmatically, capture and handle the return value:
   ```python
   exit_code = main(['generate', '--help'])
   if exit_code != 0:
       # Handle the error appropriately
   ```

2. **Validate arguments before passing them.** If you're building wrappers around the CLI, sanitize user input and use argument allowlists rather than passing arbitrary strings to `main()`.

3. **Test in realistic environments.** Run CLI tests in containers or virtual environments that mirror your deployment setup to catch environment-specific issues early.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
