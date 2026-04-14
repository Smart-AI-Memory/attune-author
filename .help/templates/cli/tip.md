---
type: tip
feature: cli
depth: tip
generated_at: 2026-04-14T14:10:01.302961+00:00
source_hash: 4ac30d5131e33f6a69817200fcda2b4abf2333630a486563d638d8630c15d2a9
status: generated
---

# Use the main() function for programmatic CLI access

Call `main()` directly instead of invoking the command-line binary when you need to run attune-author from Python code. This gives you better error handling and avoids subprocess overhead, though you lose shell features like pipes and redirects.

The `main()` function accepts an optional `argv` parameter and returns an integer exit code, making it easy to test different command combinations or integrate into larger Python workflows.
