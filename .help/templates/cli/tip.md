---
type: tip
feature: cli
depth: tip
generated_at: 2026-04-11T04:57:51.130645+00:00
source_hash: a51e03870f89add843bf351e1f8f4a23c174c46122a5a2780eca70d10e873bce
status: generated
---

# Use attune-author CLI through the main() function

## Recommendation

Call `main(argv)` instead of running the CLI as a subprocess when integrating attune-author into other Python tools.

**Why:** Direct function calls preserve stack traces and avoid the overhead of process spawning, making debugging much easier.

**Tradeoff:** You lose shell features like pipes and redirection, but gain programmatic control over arguments and output handling.

## Example

```python
from attune_author.cli import main

# Instead of subprocess.run(["attune-author", "status"])
exit_code = main(["status"])
```

## Source files

- `src/attune_author/cli.py`

**Tags:** `cli`, `commands`, `entrypoint`
