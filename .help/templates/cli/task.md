---
type: task
feature: cli
depth: task
generated_at: 2026-04-12T04:53:39.048815+00:00
source_hash: b40b5cd02e5e4ea8d4a6bf7a3a528cdf03aee2a0e01db1dbdc1a9be426d9af1f
status: generated
---

# Work with cli

Use the CLI when you need to run attune-author commands from the terminal for bootstrapping projects, generating documentation, checking status, or performing maintenance tasks.

## Prerequisites

- Access to the project source code
- Python environment with attune-author installed

## Run the CLI

1. **Execute the main command.**
   Run `attune-author` from your terminal to see available subcommands:
   ```bash
   attune-author --help
   ```

2. **Choose your subcommand.**
   Select from the available options:
   - `bootstrap` - Initialize a new project
   - `generate` - Create documentation
   - `status` - Check project state
   - `maintain` - Perform maintenance tasks

3. **Run your chosen command.**
   Execute the subcommand with any required arguments:
   ```bash
   attune-author <subcommand> [options]
   ```

## Modify CLI behavior

1. **Locate the main entry point.**
   Open `src/attune_author/cli.py` and find the `main()` function, which serves as the CLI entry point.

2. **Review the current command structure.**
   Examine how existing subcommands are defined and their argument parsing to understand the pattern.

3. **Implement your changes.**
   Modify the argument parsing, add new subcommands, or update existing command behavior while maintaining the established error handling and logging patterns.

4. **Test your modifications.**
   Run the CLI tests to verify your changes work correctly:
   ```bash
   pytest -k "cli"
   ```

## Verify success

The CLI works correctly when:
- `attune-author --help` displays the expected subcommands
- Each subcommand executes without errors
- All CLI tests pass

## Key files

- `src/attune_author/cli.py` - Main CLI implementation
