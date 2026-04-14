---
type: tip
feature: preamble
depth: tip
generated_at: 2026-04-14T16:13:32.705909+00:00
source_hash: 4b502067010f8654195a342453668853d3f231f8ca87c84c441ba90da1f2b064
status: generated
---

# Use `get_preamble()` to build contextual help introductions

## Recommendation

Call `get_preamble(feature_name)` when you need a concise, contextual introduction for any workflow skill. This function returns a one-line summary tailored to the current project state and recent activity.

## Why this works

Preambles adapt to what you're actually doing instead of showing generic help text, making guidance feel relevant rather than boilerplate.

## Related functions

Use `get_related_preambles()` to find contextually similar features when users need alternatives or next steps — it returns up to 3 related preambles based on shared tags.
