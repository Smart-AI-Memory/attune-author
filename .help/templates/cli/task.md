---
type: task
feature: cli
depth: task
generated_at: 2026-04-11T04:56:56.952770+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# Work with cli

Use the CLI when you need to run attune-author commands for bootstrapping projects, generating content, checking status, or performing maintenance tasks.

## Prerequisites

- Access to the project source code
- Python environment with attune-author installed

## Run the CLI

1. **Execute the main entry point.**
   Run the CLI through the `main()` function in `src/attune_author/cli.py`:
   ```bash
   python -m attune_author [subcommand] [options]
   ```

2. **Choose your subcommand.**
   The CLI provides subcommands for:
   - `bootstrap` - Initialize a new project
   - `generate` - Create content from templates
   - `status` - Check project state
   - `maintain` - Perform maintenance operations

3. **Verify the command executed.**
   Check the command's exit code and output to confirm it ran successfully. The `main()` function returns 0 for success or a non-zero exit code for errors.

## Modify CLI behavior

1. **Locate the main function.**
   Open `src/attune_author/cli.py` and find the `main(argv: list[str] | None = None) -> int` function.

2. **Add your changes.**
   Modify argument parsing, subcommand routing, or error handling within the `main()` function while preserving the existing command structure.

3. **Test your modifications.**
   Run the CLI tests to verify your changes work correctly:
   ```bash
   pytest -k "cli"
   ```

The CLI is working correctly when it accepts your subcommands, processes arguments as expected, and returns appropriate exit codes.

## Key files

- `src/attune_author/cli.py`
