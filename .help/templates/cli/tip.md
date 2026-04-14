---
type: tip
feature: cli
depth: tip
generated_at: 2026-04-14T16:14:59.237714+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Use the main() function to test CLI behavior programmatically

Pass an explicit `argv` list to `main()` instead of relying on `sys.argv` when testing or embedding the CLI. This lets you control exactly what arguments the CLI processes without modifying global state.

```python
# Test specific subcommands
exit_code = main(['generate', '--help'])

# Test with custom arguments
exit_code = main(['bootstrap', 'my-project'])
```

The function returns an integer exit code, making it easy to verify success or failure in automated tests. Without this approach, you'd need to capture `sys.argv` and restore it manually, which is error-prone and harder to parallelize.
