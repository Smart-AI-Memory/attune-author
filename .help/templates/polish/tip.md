---
type: tip
feature: polish
depth: tip
generated_at: 2026-04-14T14:00:51.150314+00:00
source_hash: cc9d97e96d238e30cf1d9fe96dacf73df94080aa66763e646494a334efc5ce52
status: generated
---

# Tip: working effectively with polish

## Recommendation

Use `build_source_summary()` to create grounded prompts before calling `polish_template()`. The polish system relies on accurate source summaries to avoid hallucinating features that don't exist in your code.

## Why

Raw generated templates often contain generic advice like "follow existing patterns" — the source summary gives the LLM concrete patterns to reference instead, producing documentation that matches your actual API.

## Tradeoff

Building comprehensive source summaries adds overhead to the polish pass, but skipping this step typically produces bland, unhelpful output that reads like filler content.
