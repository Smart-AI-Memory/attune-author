---
type: troubleshooting
feature: cli
depth: troubleshooting
generated_at: 2026-04-14T14:09:38.200628+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Troubleshoot cli

## Before you start

The attune-author CLI provides command-line access to documentation authoring tools. When issues occur, they typically manifest as the tool failing to start, crashing during execution, or producing unexpected output.

## Symptom table

| If you observe | Check |
|----------------|-------|
| Command not found or import errors | Verify `attune-author` is installed and in your PATH |
| Crashes with traceback | Review the Python traceback for the exact failure location in `main()` |
| Wrong command behavior | Confirm you're using the correct subcommand syntax |
| Silent exit with no output | Check the return code from `main()` — non-zero indicates failure |

## Step-by-step diagnosis

1. **Test basic installation.**
   Run `attune-author --help` to confirm the CLI loads correctly. If this fails, the issue is with installation or environment setup, not command logic.

2. **Isolate the failing command.**
   Strip your command down to the minimum arguments that reproduce the problem. Test each subcommand individually to narrow the scope.

3. **Check the entry point.**
   The `main()` function in `src/attune_author/cli.py` handles all command parsing and delegation. Add print statements or use a debugger to trace execution through this function.

4. **Review argument parsing.**
   Most CLI failures stem from unexpected argument combinations or malformed inputs. Verify your command syntax matches what the parser expects.

## Common fixes

- **Reinstall the package.** If `attune-author` command is not found, reinstall with `pip install -e .` from the project root to ensure the entry point is registered.

- **Check Python version compatibility.** The CLI requires compatible Python version. Verify with `python --version` that you meet the minimum requirements.

- **Clear your terminal cache.** Some shells cache command locations. Run `hash -r` (bash/zsh) or restart your terminal if the command was recently installed.

- **Validate file permissions.** If the CLI fails when accessing files, check that you have read/write permissions for the target directories.

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
