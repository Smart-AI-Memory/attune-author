"""CLI entry point for attune-author.

Provides commands for help system initialization, staleness
checking, template generation, and document generation.

Usage:
    attune-author init              # Bootstrap .help/
    attune-author status            # Show staleness report
    attune-author generate <feat>   # Generate templates
    attune-author regenerate        # Regenerate stale
    attune-author docs <path>       # Generate docs (AI)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from attune_author.mcp.path_validation import validate_file_path

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level argparse parser for attune-author.

    Keeping parser construction in its own function lets unit
    tests exercise argument parsing without invoking the full
    ``main()`` dispatch and lets ``main()`` itself stay short.

    Returns:
        A fully-configured parser with every subcommand wired.
    """
    parser = argparse.ArgumentParser(
        prog="attune-author",
        description="Documentation authoring and maintenance for the attune ecosystem.",
        epilog=(
            "Examples:\n"
            "  attune-author init                  Scan project and propose features\n"
            "  attune-author status                Show which templates are stale\n"
            "  attune-author generate auth         Generate templates for 'auth' feature\n"
            "  attune-author regenerate --dry-run  List stale features without regenerating\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging.",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_init = sub.add_parser(
        "init",
        help="Initialize .help/ in the current project",
        description=(
            "Scan the project and propose a features.yaml manifest listing "
            "each subsystem's source files. Safe to re-run: exits cleanly if "
            "a manifest already exists."
        ),
    )
    p_init.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: %(default)s).",
    )

    p_status = sub.add_parser(
        "status",
        help="Show staleness report",
        description=(
            "Report which features have help templates that are out of sync "
            "with their source files, based on content hashes stored in "
            "template frontmatter."
        ),
    )
    p_status.add_argument(
        "--help-dir",
        default=".help",
        help="Path to .help/ directory (default: %(default)s).",
    )
    p_status.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: %(default)s).",
    )

    p_gen = sub.add_parser(
        "generate",
        help="Generate templates for a feature",
        description=(
            "Render help templates (concept, task, reference, quickstart, "
            "etc.) for a single feature from its source files. Skips files "
            "marked 'status: manual' in frontmatter unless --overwrite is given."
        ),
    )
    # Positional is optional so we can print a contextual error
    # (with the list of available features) instead of argparse's
    # terse "the following arguments are required" message.
    p_gen.add_argument("feature", nargs="?", help="Feature name to generate.")
    p_gen.add_argument(
        "--help-dir",
        default=".help",
        help="Path to .help/ directory (default: %(default)s).",
    )
    p_gen.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: %(default)s).",
    )
    p_gen.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite templates marked 'status: manual' in their frontmatter.",
    )
    p_gen.add_argument(
        "--no-rag",
        action="store_true",
        help=(
            "Disable RAG grounding during polish. By default, when "
            "attune-author[rag] is installed the polish pass consults "
            "existing attune-help templates for style / naming "
            "references. Set this flag (or ATTUNE_AUTHOR_RAG=0 in the "
            "environment) to skip retrieval and use the bare prompt."
        ),
    )
    p_gen.add_argument(
        "--all-kinds",
        action="store_true",
        help=(
            "Generate every template kind: .help/ kinds (concept, task, "
            "reference, quickstart, faq, error, warning, tip, note, "
            "comparison, troubleshooting) plus project-doc kinds that "
            "write to docs/ (how-to, tutorial, cli-reference, "
            "architecture). Use this for full help and docs coverage."
        ),
    )

    p_regen = sub.add_parser(
        "regenerate",
        help="Regenerate all stale templates",
        description=(
            "Detect stale features (by source hash mismatch) and regenerate "
            "their templates. Use --dry-run to preview without writing."
        ),
    )
    p_regen.add_argument(
        "--help-dir",
        default=".help",
        help="Path to .help/ directory (default: %(default)s).",
    )
    p_regen.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: %(default)s).",
    )
    p_regen.add_argument(
        "--dry-run",
        action="store_true",
        help="Report stale features without regenerating.",
    )

    p_docs = sub.add_parser(
        "docs",
        help="Generate docs from source (requires [ai])",
        description=(
            "Generate documentation from a source file or module using the "
            "three-stage LLM pipeline (outline, write, review). Requires the "
            "[ai] extra and ANTHROPIC_API_KEY in the environment."
        ),
    )
    # Optional so the handler can print a contextual usage hint.
    p_docs.add_argument("target", nargs="?", help="Source file or module to document.")
    p_docs.add_argument("--output", "-o", help="Output file path (default: stdout).")
    p_docs.add_argument(
        "--doc-type",
        default="api-reference",
        help="Documentation type (default: %(default)s).",
    )
    p_docs.add_argument(
        "--audience",
        default="developers",
        help="Target audience (default: %(default)s).",
    )

    return parser


def _dispatch(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Run the subcommand selected on ``args``.

    Split out from :func:`main` so the dispatch table stays
    testable in isolation and so :func:`main` is thin enough
    to read at a glance.

    Args:
        args: Parsed arguments.
        parser: The top-level parser, used for the ``--help``
            fallback when no subcommand is given.

    Returns:
        Process exit code.
    """
    if not args.command:
        _print_welcome()
        return 0

    handlers = {
        "init": _cmd_init,
        "status": _cmd_status,
        "generate": _cmd_generate,
        "regenerate": _cmd_regenerate,
        "docs": _cmd_docs,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 0

    try:
        return handler(args)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success).
    """
    # Load .env early so downstream code (polish, doc-gen) can
    # find ANTHROPIC_API_KEY without users exporting it manually.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    return _dispatch(args, parser)


def _cmd_init(args: argparse.Namespace) -> int:
    """Handle the init command."""
    from attune_author.bootstrap import proposals_to_manifest, scan_project
    from attune_author.manifest import save_manifest

    root = validate_file_path(args.project_root)
    help_dir = root / ".help"

    if (help_dir / "features.yaml").exists():
        print(f"Already initialized: {help_dir / 'features.yaml'}")
        return 0

    print(f"Scanning {root}...")
    proposals = scan_project(root)

    if not proposals:
        print("No features discovered. Create .help/features.yaml manually.")
        return 0

    print(f"\nDiscovered {len(proposals)} features:\n")
    for p in proposals:
        conf = {"high": "+", "medium": "~", "low": "?"}
        marker = conf.get(p.confidence, "?")
        print(f"  [{marker}] {p.name} — {p.description}")
        print(f"      files: {', '.join(p.files)}")

    manifest = proposals_to_manifest(proposals)
    path = save_manifest(manifest, help_dir)
    print(f"\nSaved {len(proposals)} features to {path}")
    print("Edit .help/features.yaml to refine, then run: attune-author generate <feature>")

    return 0


def _print_missing_manifest_hint(help_dir: Path) -> None:
    """Print a friendly hint when features.yaml is missing."""
    print(
        f"No manifest at {help_dir / 'features.yaml'}. Run `attune-author init` first.",
        file=sys.stderr,
    )


def _cmd_status(args: argparse.Namespace) -> int:
    """Handle the status command."""
    from attune_author.maintenance import format_status_report
    from attune_author.manifest import load_manifest
    from attune_author.staleness import check_staleness

    root = validate_file_path(args.project_root)
    help_dir = validate_file_path(args.help_dir)

    try:
        manifest = load_manifest(help_dir)
    except FileNotFoundError:
        _print_missing_manifest_hint(help_dir)
        return 1

    report = check_staleness(manifest, help_dir, root)
    print(format_status_report(report, help_dir))

    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    """Handle the generate command."""
    from attune_author.generator import generate_feature_templates
    from attune_author.manifest import load_manifest

    root = validate_file_path(args.project_root)
    help_dir = validate_file_path(args.help_dir)

    if not args.feature:
        _print_generate_usage(help_dir)
        return 1

    try:
        manifest = load_manifest(help_dir)
    except FileNotFoundError:
        _print_missing_manifest_hint(help_dir)
        return 1

    feature = manifest.features.get(args.feature)
    if not feature:
        print(f"Feature '{args.feature}' not found in manifest.", file=sys.stderr)
        if manifest.features:
            print(
                f"Available: {', '.join(sorted(manifest.features))}",
                file=sys.stderr,
            )
        return 1

    from attune_author.generator import _ALL_TEMPLATE_NAMES

    result = generate_feature_templates(
        feature=feature,
        help_dir=help_dir,
        project_root=root,
        depths=list(_ALL_TEMPLATE_NAMES) if args.all_kinds else None,
        overwrite=args.overwrite,
        use_rag=not args.no_rag,
    )

    if result.templates:
        print(f"Generated {len(result.templates)} templates for '{args.feature}':")
        for t in result.templates:
            print(f"  {t.path}")
    else:
        print("No templates generated (all may be manual).")

    return 0


def _cmd_regenerate(args: argparse.Namespace) -> int:
    """Handle the regenerate command."""
    from attune_author.maintenance import run_maintenance

    root = validate_file_path(args.project_root)
    help_dir = validate_file_path(args.help_dir)

    try:
        result = run_maintenance(
            help_dir=help_dir,
            project_root=root,
            dry_run=args.dry_run,
        )
    except FileNotFoundError:
        _print_missing_manifest_hint(help_dir)
        return 1

    if args.dry_run:
        print(f"Stale features: {result.stale_count}")
        for name in result.staleness.stale_features:
            print(f"  - {name}")
    else:
        print(f"Regenerated: {result.regenerated_count}")
        if result.failed:
            print(f"Failed: {', '.join(result.failed)}")

    return 0


def _cmd_docs(args: argparse.Namespace) -> int:
    """Handle the docs command."""
    if not args.target:
        _print_docs_usage()
        return 1

    try:
        from attune_author.doc_gen import DocGenConfig, generate_docs
    except ImportError:
        print(
            "Doc generation requires the [ai] extra:\n  pip install 'attune-author[ai]'",
            file=sys.stderr,
        )
        return 1

    target = str(validate_file_path(args.target))
    output = str(validate_file_path(args.output)) if args.output else None

    config = DocGenConfig(
        doc_type=args.doc_type,
        audience=args.audience,
    )

    result = generate_docs(
        target=target,
        config=config,
        output_path=output,
    )

    if args.output:
        print(f"Documentation written to {args.output}")
    else:
        print(result.content)

    return 0


def _get_version() -> str:
    """Get package version."""
    try:
        from attune_author import __version__

        return __version__
    except ImportError:
        return "dev"


_WELCOME_HEADER = "attune-author — documentation authoring for the attune ecosystem"
_MAX_FEATURES_IN_WELCOME = 8


def _print_welcome() -> None:
    """Print the zero-arg welcome screen.

    Detects whether ``.help/features.yaml`` exists in the current
    working directory and adjusts the suggested next command. A
    missing or broken manifest falls through to the "not set up
    yet" path so a stranger running the tool cold never sees a
    traceback.
    """
    print(_WELCOME_HEADER)
    print()

    features = _load_feature_names_for_welcome()
    if features is None:
        print("It looks like this project isn't set up yet.")
        print()
        print("Get started:")
        print("  attune-author init        Scan your project and propose features")
        print()
        print("Other commands: status, generate, regenerate, docs")
        print("Run `attune-author --help` for the full reference.")
        return

    shown = features[:_MAX_FEATURES_IN_WELCOME]
    suffix = ", …" if len(features) > _MAX_FEATURES_IN_WELCOME else ""
    print(f"Found {len(features)} features in .help/features.yaml:")
    print(f"  {', '.join(shown)}{suffix}")
    print()
    print("Try:")
    print("  attune-author status              Check for stale docs")
    print("  attune-author generate <feature>  Generate templates for a feature")
    print()
    print("Run `attune-author --help` for the full reference.")


def _print_generate_usage(help_dir: Path) -> None:
    """Print a contextual usage hint for `generate` with no feature.

    Tries to list the feature names from the manifest so the user
    sees exactly what they can pass. Falls back to a generic hint
    if the manifest is missing or unreadable.
    """
    print("Usage: attune-author generate <feature>", file=sys.stderr)
    print("  Generates concept/task/reference templates for a feature.", file=sys.stderr)

    try:
        from attune_author.manifest import load_manifest

        manifest = load_manifest(help_dir)
    except Exception:  # noqa: BLE001
        print(
            f"\nNo manifest found at {help_dir / 'features.yaml'}. "
            "Run `attune-author init` first.",
            file=sys.stderr,
        )
        return

    if not manifest.features:
        print(
            "\nThe manifest has no features yet — edit "
            f"{help_dir / 'features.yaml'} or re-run `attune-author init`.",
            file=sys.stderr,
        )
        return

    names = sorted(manifest.features.keys())
    print(f"\nAvailable features: {', '.join(names)}", file=sys.stderr)


def _print_docs_usage() -> None:
    """Print a contextual usage hint for `docs` with no target."""
    print("Usage: attune-author docs <target> [--output FILE]", file=sys.stderr)
    print(
        "  Generates documentation for a Python file or module using AI.",
        file=sys.stderr,
    )
    print("  Example: attune-author docs src/myapp/auth.py", file=sys.stderr)
    print("  Requires the [ai] extra: pip install 'attune-author[ai]'", file=sys.stderr)


def _load_feature_names_for_welcome() -> list[str] | None:
    """Return a sorted list of feature names, or None if unusable.

    Returns None when ``.help/features.yaml`` is missing, unreadable,
    malformed, or contains zero features — any of which means the
    welcome screen should treat the project as "not set up yet".
    Swallows every exception on purpose: this is UI, not a loader.
    """
    help_dir = Path(".help")
    if not (help_dir / "features.yaml").exists():
        return None

    try:
        from attune_author.manifest import load_manifest

        manifest = load_manifest(help_dir)
    except Exception:  # noqa: BLE001
        # INTENTIONAL: any failure here means we should show the
        # "not set up yet" screen — a corrupt manifest must not
        # crash a bare `attune-author` invocation.
        return None

    names = sorted(manifest.features.keys())
    return names or None


if __name__ == "__main__":
    sys.exit(main())
