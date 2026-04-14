---
type: task
feature: cli
depth: task
generated_at: 2026-04-14T14:09:07.274964+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Work with cli

Use the attune-author CLI when you need to run documentation authoring commands from the terminal with subcommands for bootstrap, generate, status, and maintain.

## Prerequisites

- Access to the project source code
- Python environment with attune-author installed

## Run the CLI

1. **Execute the main entry point.**
   Run the CLI by calling the main function:
   ```python
   from attune_author.cli import main
   exit_code = main()
   ```

2. **Pass command-line arguments.**
   Provide arguments as a list to customize behavior:
   ```python
   exit_code = main(['generate', '--output', 'docs/'])
   ```

3. **Verify successful execution.**
   Check that the function returns `0` for success or a non-zero exit code for errors.

## Modify CLI behavior

1. **Locate the main function.**
   Open `src/attune_author/cli.py` and find the `main()` function that serves as the CLI entry point.

2. **Review the current implementation.**
   Examine the function signature, parameters, and return type to understand how it processes command-line arguments.

3. **Update the function logic.**
   Modify the `main()` function following the existing code patterns for argument parsing, error handling, and return codes.

4. **Test your changes.**
   Run the CLI tests to verify your modifications work correctly:
   ```bash
   pytest -k "cli"
   ```

## Verify the CLI works

Confirm your changes by running the CLI and checking that:
- The welcome header displays: "attune-author — documentation authoring for the attune ecosystem"
- Commands execute without errors
- The function returns appropriate exit codes

## Key files

- `src/attune_author/cli.py` — Contains the main CLI entry point
