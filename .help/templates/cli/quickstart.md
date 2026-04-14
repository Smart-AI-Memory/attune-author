---
type: quickstart
feature: cli
depth: quickstart
generated_at: 2026-04-14T14:09:55.081981+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Quickstart: cli

Run the attune-author command-line tool to see available commands:

```bash
python -m attune_author.cli
```

Expected output:
```
attune-author — documentation authoring for the attune ecosystem

Available commands:
  bootstrap  Set up a new documentation project
  generate   Build documentation from source
  status     Check project health
  maintain   Update and clean documentation
```

## Run your first command

1. **Check what commands are available.** The CLI shows you all subcommands when you run it without arguments.

2. **Try the status command** to see your current project state:
   ```bash
   python -m attune_author.cli status
   ```

3. **Bootstrap a new project** if you don't have one:
   ```bash
   python -m attune_author.cli bootstrap
   ```

## Next steps

Run `python -m attune_author.cli generate` to build your documentation from source code.
