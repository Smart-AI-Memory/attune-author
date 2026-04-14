---
type: task
feature: cli
depth: task
generated_at: 2026-04-14T16:14:02.965746+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Work with cli

Use the attune-author CLI when you need to run documentation authoring commands from the command line, including bootstrap, generate, status, and maintain operations.

## Prerequisites

- Access to the project source code
- Python environment with attune-author installed
- Familiarity with `src/attune_author/cli.py`

## Run the CLI

1. **Execute the main entry point.**
   Run the CLI through the `main()` function:
   ```bash
   python -m attune_author
   ```

2. **Pass command arguments.**
   Provide subcommands and options as needed:
   ```bash
   python -m attune_author generate --help
   ```

3. **Verify the welcome message appears.**
   The CLI displays "attune-author — documentation authoring for the attune ecosystem" when started successfully.

## Modify CLI behavior

1. **Locate the main function.**
   Open `src/attune_author/cli.py` and find the `main(argv: list[str] | None = None) -> int` function that serves as the CLI entry point.

2. **Update command handling.**
   Modify the argument parsing logic within `main()` to add new subcommands or change existing behavior.

3. **Test your changes.**
   Run the CLI with your modifications:
   ```bash
   python -m attune_author [your-command]
   ```

4. **Run targeted tests.**
   Verify your changes don't break existing functionality:
   ```bash
   pytest -k "cli"
   ```

## Verify success

The task succeeds when:
- The CLI runs without errors
- Your new commands or modifications work as expected
- All CLI-related tests pass

## Key files

- `src/attune_author/cli.py` — Main CLI implementation and entry point
