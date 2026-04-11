---
type: tip
feature: bootstrap
depth: tip
generated_at: 2026-04-11T04:52:48.819121+00:00
source_hash: ba3e45edbaf44fba671f221a61e39cae7381b0b1c8ce9a02129f76b20bc6f331
status: generated
---

# Tip: Run scan_project first to understand your codebase structure

## The recommendation

Start feature discovery by calling `scan_project()` on your project root, then review the `ProposedFeature` objects before converting them to a manifest.

## Why this helps

Scanning reveals what the bootstrap module thinks your project structure contains, which often differs from what you expect — catching mismatches early saves debugging time later.

## The tradeoff

Manual review of proposals adds an extra step, but automatic conversion with `proposals_to_manifest()` can generate manifests that don't match your project's actual organization.

**Tags:** `setup`, `scanning`, `manifest`
