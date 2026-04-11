---
type: tip
feature: polish
depth: tip
generated_at: 2026-04-11T04:49:26.160278+00:00
source_hash: 024a299e9a8252b83e070c5a5297e1292dd243e8eddc631dcf298bae31fb8dc0
status: generated
---

# Use strict mode when polish quality matters

Enable strict mode in `polish_template()` to catch LLM failures early rather than silently accepting low-quality output. This raises `PolishError` when the polish pass produces malformed or off-topic content, letting you retry or fall back to the original template.

The tradeoff is slower execution since you'll need to handle failures, but strict mode prevents publishing broken documentation when the LLM has a bad day.
