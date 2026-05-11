# Tasks — skill-export evangelism

## Phase 0 — Topic angle (Patrick's call)

- [ ] **0.1** Patrick picks the blog topic angle. Candidates:
  - **"Your team's docs as Claude Code skills"** — generalist
    framing, broad appeal
  - **"From RAG to skills: when to pick which"** —
    architectural framing, positions Smart-AI-Memory as an
    ecosystem thinker
  - **"Building Claude Code skills from existing
    documentation"** — implementation-focused
  - **Patrick's own pitch** — something different

Phase 1 doesn't start until 0.1 is decided.

## Phase 1 — Pick the worked-example corpus

- [ ] **1.1** Candidates:
  - attune-help's own templates (meta but easy)
  - Smart-AI-Memory blog post archive (if available)
  - A representative public docs corpus (e.g., a small open-
    source project's docs)
- [ ] **1.2** Run `attune-author skill-export` against the
      chosen corpus
- [ ] **1.3** Inspect the generated SKILL.md bundles for
      quality — are the descriptions accurate? Do the
      triggers make sense?
- [ ] **1.4** Iterate if needed (re-run with different
      `--corpus` / `--depth` flags)

## Phase 2 — Publish the example

- [ ] **2.1** Decide where the example lives:
  - `attune-ai/plugin/skills/example-help-export/` (visible
    to attune-ai users)
  - A new `attune-skill-examples/` repo (cleaner separation)
  - Inline in the blog post itself
- [ ] **2.2** Publish + cross-link

## Phase 3 — Blog post

- [ ] **3.1** Draft outline per the chosen topic angle
- [ ] **3.2** Write the technical content (commands, screenshots,
      before/after)
- [ ] **3.3** Review for accuracy — does the example actually
      work as described?
- [ ] **3.4** Publish on Smart-AI-Memory blog or a public
      surface
- [ ] **3.5** Add link from attune-author README

## Phase 4 — Track signal

- [ ] **4.1** Watch GitHub stars / referrals / community
      mentions over 2-4 weeks post-publish
- [ ] **4.2** Note any user feedback in `decisions.md`
- [ ] **4.3** Decide whether to write a Part 2 or call the
      evangelism push complete

## Out of scope

- Other attune-author features (regenerate, polish, etc.) —
  separate evangelism pieces if warranted
- Multi-language SKILL.md generation
- Auto-publishing to Anthropic skill marketplaces (if such a
  thing exists / arrives later)
