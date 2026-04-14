---
type: tip
feature: polish
depth: tip
generated_at: 2026-04-14T16:05:46.083180+00:00
source_hash: 39a4215a31cf6bfa17f5b898ad071827d406cbe4dc8d2744f17fe7fd680d6891
status: generated
---

# Tip: working effectively with polish

## Recommendation

Enable strict mode when developing polish prompts by setting `ATTUNE_AUTHOR_STRICT_POLISH=1` in your environment.

## Why

Strict mode makes `polish_template()` raise `PolishError` on LLM failures instead of returning degraded output, so you catch prompt issues during development rather than in production.

## Tradeoff

Your tests will be more brittle to API outages, but you'll ship higher-quality templates.
