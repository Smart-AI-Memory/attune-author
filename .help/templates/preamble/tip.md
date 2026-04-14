---
type: tip
feature: preamble
depth: tip
generated_at: 2026-04-14T14:08:34.820756+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Use `get_preamble()` to set context for workflow skills

## The recommendation

Call `get_preamble(feature_name)` to retrieve a one-liner that sets context before executing workflow skills. This contextual header helps orient users about what the feature does and why they might need it.

## Why this works

Preambles bridge the gap between abstract feature names and concrete user intent, making workflows feel more conversational and goal-oriented rather than robotic.

## The tradeoff

You'll need to maintain preamble content as features evolve — stale context is worse than no context.

## Related functions

- `get_related_preambles()` — Find preambles for similar features when you want to suggest alternatives

**Tags:** `context`, `rendering`, `workflow`
