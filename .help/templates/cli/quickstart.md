---
type: quickstart
feature: cli
depth: quickstart
generated_at: 2026-04-11T04:57:44.528870+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# Quickstart: cli

Run the attune-author command-line interface to see available subcommands:

```bash
python -m attune_author.cli --help
```

## Prerequisites

- Python environment with attune-author installed
- Terminal or command prompt access

## Run your first command

1. **Check the CLI is working** by displaying the help menu:
   ```bash
   python -m attune_author.cli --help
   ```

   You should see output listing the available subcommands: bootstrap, generate, status, and maintain.

2. **Run a status check** to see the current state:
   ```bash
   python -m attune_author.cli status
   ```

3. **Verify the command executed** by checking the return code. A successful run returns 0.

## Expected output

The help command shows:
```
usage: attune_author.cli [-h] {bootstrap,generate,status,maintain} ...

Command-line entry point for attune-author

positional arguments:
  {bootstrap,generate,status,maintain}
    bootstrap           Initialize new project
    generate           Create documentation
    status             Show current status
    maintain           Update existing files
```

## Next steps

Try `python -m attune_author.cli bootstrap --help` to initialize your first documentation project.
