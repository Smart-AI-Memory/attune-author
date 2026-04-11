"""Regenerate the .help/ template tree for attune-author.

This is the dogfood entry point: attune-author uses its own
pipeline to produce its own documentation. Run this script
whenever the source layout, the meta-templates, or the
polish prompts change in ways that would alter the output.

Usage
-----

    python scripts/regenerate_help.py

The script reads ``.help/features.yaml``, generates all 11
template kinds for every feature listed there, and writes
the polished output to ``.help/templates/<feature>/<kind>.md``.

Polish requires ``ANTHROPIC_API_KEY`` to be set in the
environment. Without it, the script falls back to the raw
Jinja2 drafts and prints a warning. You can also set
``ATTUNE_AUTHOR_STRICT_POLISH=1`` to make polish failures
hard errors instead of silent fallbacks.

To target a subset of features::

    python scripts/regenerate_help.py --features generator polish

To skip polish even when an API key is present::

    python scripts/regenerate_help.py --no-polish
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

from attune_author.generator import (
    _ALL_TEMPLATE_NAMES,
    GenerationResult,
    generate_feature_templates,
)
from attune_author.manifest import load_manifest

logger = logging.getLogger("regenerate_help")

REPO_ROOT = Path(__file__).resolve().parent.parent
HELP_DIR = REPO_ROOT / ".help"


def main() -> int:
    """Regenerate every template kind for every feature.

    Returns:
        Process exit code (0 on success, 1 on any failure).
    """
    parser = argparse.ArgumentParser(
        description="Regenerate attune-author's own help templates",
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=None,
        help="Subset of feature names to regenerate (default: all)",
    )
    parser.add_argument(
        "--no-polish",
        action="store_true",
        help="Skip the LLM polish pass even if an API key is set",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    if not HELP_DIR.exists():
        logger.error("Missing .help/ directory at %s", HELP_DIR)
        return 1

    try:
        manifest = load_manifest(HELP_DIR)
    except FileNotFoundError as exc:
        logger.error("Cannot load manifest: %s", exc)
        return 1
    except ValueError as exc:
        logger.error("Manifest validation failed: %s", exc)
        return 1

    target_features = _resolve_targets(manifest.features, args.features)
    if not target_features:
        return 1

    if args.no_polish:
        # Temporarily clear the API key for the duration of
        # this run so the generator's _maybe_polish() takes
        # the lenient fallback path. We restore on exit.
        original = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            return _run(target_features)
        finally:
            if original is not None:
                os.environ["ANTHROPIC_API_KEY"] = original
    else:
        return _run(target_features)


def _resolve_targets(
    all_features: dict,
    requested: list[str] | None,
) -> list:
    """Pick which features to regenerate.

    Args:
        all_features: Full feature map from the manifest.
        requested: User-supplied filter, or None for all.

    Returns:
        List of Feature objects to process. Empty on error.
    """
    if requested is None:
        return list(all_features.values())

    missing = [name for name in requested if name not in all_features]
    if missing:
        logger.error(
            "Unknown feature(s): %s. Available: %s",
            ", ".join(missing),
            ", ".join(sorted(all_features.keys())),
        )
        return []

    return [all_features[name] for name in requested]


def _run(features: list) -> int:
    """Generate every template kind for every feature.

    Args:
        features: List of Feature objects to process.

    Returns:
        Process exit code.
    """
    have_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if have_key:
        logger.info(
            "Polish enabled — %s × %d kinds = %d templates",
            len(features),
            len(_ALL_TEMPLATE_NAMES),
            len(features) * len(_ALL_TEMPLATE_NAMES),
        )
    else:
        logger.warning(
            "ANTHROPIC_API_KEY not set — output will be raw "
            "Jinja2 drafts (run again with the key for polish)"
        )

    total_templates = 0
    failures: list[tuple[str, str, str]] = []
    started = time.perf_counter()

    for feature in features:
        feature_started = time.perf_counter()
        logger.info("Generating %s …", feature.name)

        try:
            result: GenerationResult = generate_feature_templates(
                feature=feature,
                help_dir=HELP_DIR,
                project_root=REPO_ROOT,
                depths=list(_ALL_TEMPLATE_NAMES),
                overwrite=True,
            )
        except Exception as exc:  # noqa: BLE001
            # INTENTIONAL: continue with the next feature so
            # one bad feature does not block the whole run.
            logger.error("  failed: %s", exc)
            failures.append((feature.name, "<all>", str(exc)))
            continue

        elapsed = time.perf_counter() - feature_started
        total_templates += len(result.templates)
        logger.info(
            "  → %d templates in %.1fs",
            len(result.templates),
            elapsed,
        )

    elapsed_total = time.perf_counter() - started
    logger.info(
        "Done. %d templates generated in %.1fs.",
        total_templates,
        elapsed_total,
    )

    if failures:
        logger.error("%d failure(s):", len(failures))
        for feature_name, kind, msg in failures:
            logger.error("  %s/%s: %s", feature_name, kind, msg)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
