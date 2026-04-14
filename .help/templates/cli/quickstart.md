---
type: quickstart
feature: cli
depth: quickstart
generated_at: 2026-04-14T16:14:52.675752+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Quickstart: cli

Run the attune-author CLI to access documentation authoring commands for the attune ecosystem.

```bash
python -m attune_author.cli
```

You'll see the welcome header and available commands:

```
attune-author — documentation authoring for the attune ecosystem
```

## Prerequisites

- Python environment with attune-author installed
- Command line access

## Run your first command

1. **Check the CLI status.** Run the main entry point to see what subcommands are available:
   ```bash
   python -m attune_author.cli
   ```

2. **Try a specific subcommand.** Use one of the available commands like `status`, `bootstrap`, `generate`, or `maintain`:
   ```bash
   python -m attune_author.cli status
   ```

3. **Verify the output.** The CLI returns an integer exit code (0 for success) and displays relevant information for your chosen command.

## Next steps

Run `python -m attune_author.cli --help` to explore all available subcommands and their options.
