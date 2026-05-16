"""Smoke-test the Phase 3 faithfulness judge on one feature.

Picks the smallest feature in features.yaml (fewest source files),
regenerates its 3 core kinds (concept/task/reference), and reports
on whether the judge fired, what it scored, and whether any review
blocks were appended.

Designed for low cost — one feature × 3 kinds × Haiku 4.5 ≈ $0.03.

Usage::

    export ANTHROPIC_API_KEY=sk-ant-...
    uv run python scripts/test_faithfulness.py [feature_name]

Without a feature_name argument, the script picks the feature
with the fewest source files.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from attune_author.generator import (
    _faithfulness_telemetry,
    generate_feature_templates,
    reset_faithfulness_telemetry,
)
from attune_author.manifest import load_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
        datefmt="%H:%M:%S",
    )
    # Surface faithfulness module logs at INFO.
    logging.getLogger("attune_author.faithfulness").setLevel(logging.INFO)
    logging.getLogger("attune_author.generator").setLevel(logging.INFO)


def _pick_smallest_feature(manifest) -> str:
    candidates = sorted(
        manifest.features.values(),
        key=lambda f: len(f.files),
    )
    return candidates[0].name


def main() -> int:
    _setup_logging()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        print(
            "Export your key and re-run: export ANTHROPIC_API_KEY=sk-ant-...",
            file=sys.stderr,
        )
        return 1

    manifest = load_manifest(REPO_ROOT / ".help")
    feature_name = sys.argv[1] if len(sys.argv) > 1 else _pick_smallest_feature(manifest)
    feature = manifest.features.get(feature_name)
    if feature is None:
        print(f"ERROR: unknown feature {feature_name!r}", file=sys.stderr)
        print(f"Available: {sorted(manifest.features)}", file=sys.stderr)
        return 1

    print("\n=== Phase 3 faithfulness smoke test ===")
    print(f"Feature:       {feature_name}")
    print(f"Source files:  {feature.files}")
    print(f"Working dir:   {REPO_ROOT}")
    print()

    reset_faithfulness_telemetry()

    # Run generate from the repo root so cwd-relative resolution
    # (matched_files, project_root) lines up.
    original_cwd = Path.cwd()
    try:
        os.chdir(REPO_ROOT)
        result = generate_feature_templates(
            feature=feature,
            help_dir=REPO_ROOT / ".help",
            project_root=REPO_ROOT,
            overwrite=True,
        )
    finally:
        os.chdir(original_cwd)

    telemetry = _faithfulness_telemetry()
    print()
    print("=== Judge telemetry ===")
    print(f"  Calls:           {int(telemetry['calls'])}")
    print(f"  Skipped:         {int(telemetry['skipped'])}")
    print(f"  Estimated cost:  ${telemetry['cost_usd']:.4f}")
    print()

    review_blocks_found = 0
    print("=== Polished templates ===")
    for tmpl in result.templates:
        text = tmpl.path.read_text(encoding="utf-8")
        has_review = "## Faithfulness review" in text
        marker = "REVIEW" if has_review else "clean"
        print(f"  [{marker}] {tmpl.path.relative_to(REPO_ROOT)}")
        if has_review:
            review_blocks_found += 1

    print()
    if telemetry["calls"] == 0 and telemetry["skipped"] == 0:
        print("Judge did NOT run. Diagnostic checks:")
        print("  - Is `enabled = true` set in " "[tool.attune-author.fact-check.faithfulness]?")
        print("  - Is ATTUNE_AUTHOR_FAITHFULNESS=off in the environment?")
        return 2

    if review_blocks_found:
        print(
            f"{review_blocks_found} template(s) flagged below threshold — "
            f"check the files above for the ## Faithfulness review block."
        )
    else:
        print("All templates scored at or above threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
