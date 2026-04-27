---
type: task
feature: cli
depth: task
generated_at: 2026-04-26T19:48:40.826441+00:00
source_hash: f0f928daa13f792e7874da74f9fd669dc0e772acc208349a075625078eeb59c7
status: generated
---

# Work with cli

Use the attune-author CLI when you need to run documentation authoring commands from the terminal, including bootstrap, generate, status, and maintenance operations.

## Prerequisites

- Access to the project source code
- Python development environment set up
- Familiarity with `src/attune_author/cli.py`

## Steps

1. **Examine the CLI entry point.**
   Review the `main()` function in `src/attune_author/cli.py` to understand the current command structure and argument parsing.

2. **Identify the target functionality.**
   Locate the specific function or command handler that controls the behavior you want to modify. The `main()` function serves as the primary entry point for all CLI operations.

3. **Modify the CLI behavior.**
   Update the relevant code sections while maintaining the existing argument parsing patterns and error handling conventions used throughout the file.

4. **Test your changes.**
   Run targeted tests to verify your modifications work correctly:
   ```bash
   pytest -k "cli"
   ```

## Verification

Your CLI modifications are working correctly when:
- The command executes without syntax errors
- All existing CLI commands continue to function as expected
- New functionality responds with the expected output or behavior
- The welcome header "_WELCOME_HEADER" displays correctly when appropriate

## Key files

- `src/attune_author/cli.py` — Main CLI implementation and entry point
