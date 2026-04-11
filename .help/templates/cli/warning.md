---
type: warning
feature: cli
depth: warning
generated_at: 2026-04-11T04:57:17.325001+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# CLI cautions

## What to watch for

The attune-author CLI provides subcommands for bootstrap, generate, status, and maintain operations. While the interface appears straightforward, several characteristics of command-line tools can create unexpected behavior in production environments.

## Risk areas

**Argument parsing conflicts with shell expansion**
The CLI accepts file paths and pattern arguments that shells may expand before the program sees them. Glob patterns, spaces in filenames, and special characters can cause the CLI to receive different arguments than you intended.

**Exit code handling masks underlying errors**
The `main()` function returns integer exit codes, but intermediate exceptions or subprocess failures may get converted to generic error codes. This can make debugging difficult when the CLI is called from scripts or CI systems.

**Environment variable dependencies**
Command-line tools often inherit behavior from environment variables that aren't obvious from the command syntax. Changes to PATH, working directory, or tool-specific environment variables can alter CLI behavior without any change to your command arguments.

## How to avoid problems

1. **Quote arguments containing paths and patterns.** Always quote file paths and use explicit path separators to prevent shell expansion issues:
   ```bash
   attune-author generate "path/with spaces/file.txt"
   ```

2. **Check exit codes in scripts.** When calling the CLI from automation, explicitly check the return value and capture stderr for debugging:
   ```bash
   if ! attune-author status; then
       echo "CLI failed with exit code $?"
       exit 1
   fi
   ```

3. **Test in clean environments.** Run CLI tests in isolated environments to catch environment variable dependencies that might not be obvious in your development setup.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
