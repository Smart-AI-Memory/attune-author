# Decisions — skill-export evangelism

**Status:** Draft (2026-05-11) — gated on blog-topic greenlight
**Owner:** Patrick

---

## Problem

attune-author PR #20 shipped `skill-export` — a command that
generates Claude Code `SKILL.md` bundles from a help corpus.
This is a meaningful DX feature: anyone with private docs in
attune-help format can run one command to expose those docs as
Claude Code skills.

**But nobody knows it exists.** The feature is:

- Buried in the 0.7.0 changelog as one bullet
- Has no worked example in attune-ai's `plugin/skills/`
- Has no external write-up

Net result: a real differentiator goes unused, both internally
and externally.

## Decision

Two-part evangelism push:

1. **Blog post** — write up `skill-export` as a guide:
   "How to turn your team's private docs into Claude Code
   skills in one command." Concrete example, before/after,
   command incantation, gotchas.
2. **Worked example** — pick a credible corpus (probably
   attune-help's own docs, or a Smart-AI-Memory blog post
   archive) and publish the generated SKILL.md as an example
   in `attune-ai/plugin/skills/example-help-export/` or in a
   sibling sample repo.

## What's in scope

- Drafting the blog post outline + key technical content
- Picking the corpus for the worked example
- Generating + publishing the example skill
- Cross-linking from attune-author README to the blog +
  example

## What's NOT in scope

- Writing the full blog content tonight — Patrick wants to
  decide the topic angle first
- Changes to `skill-export` itself (it works; this is
  marketing)
- Multi-language / multi-format support
- Auto-publishing to skill marketplaces

## Alternatives considered

1. **Do nothing** — feature stays buried. Honest cost: real
   DX win goes unnoticed. Acceptable but suboptimal.
2. **Mention in next release notes only** — better than
   nothing but won't reach external readers.
3. **Build a marketing video** — too much effort for the
   audience size.

The blog + worked example pair is the lowest-effort path that
addresses both internal (devs find the example) and external
(readers find the blog) discoverability.

## Acceptance criteria

- Blog post published (in Smart-AI-Memory blog or as a doc in
  attune-author repo)
- Example SKILL.md bundle published somewhere users can find
  it
- attune-author's README links to both
- One follow-up from a user or contributor demonstrating the
  feature working in a non-attune-author corpus (signal that
  the post landed)

## Execution gate

This spec is **gated on Patrick picking a topic angle for the
blog.** Don't draft the actual post until that decision is
made. The spec itself can be approved now; execution waits.

Patrick's note: "Yes and tell me later."

---

(per-phase decisions appended once topic angle is chosen)
