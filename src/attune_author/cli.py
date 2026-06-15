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
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

from attune_author.editor_launcher import (
    PortfileData,
    SidecarStartError,
    ensure_sidecar,
)
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

    p_maint = sub.add_parser(
        "maintenance-report",
        help="Report each page's maintenance mode (auto/manual/hybrid)",
        description=(
            "Enumerate every help template and the maintenance contract it "
            "declares in frontmatter (auto, manual, or hybrid). A derived "
            "view for auditing which pages regen may overwrite versus which "
            "are human-maintained."
        ),
    )
    p_maint.add_argument(
        "--help-dir",
        default=".help",
        help="Path to .help/ directory (default: %(default)s).",
    )
    p_maint.add_argument(
        "--all",
        action="store_true",
        help="List auto pages too (default: only manual/hybrid).",
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
    # Fact-check mode per spec docs/specs/polish-fact-check/. Default
    # is "soft" (append findings to the polished file as an
    # ``## Unresolved references`` block). "strict" raises
    # FactCheckError on any error finding; "off" disables.
    # Internally sets ATTUNE_AUTHOR_FACT_CHECK; the env var path is
    # the single source of truth read by generator._run_fact_check.
    fact_check_group = p_gen.add_mutually_exclusive_group()
    fact_check_group.add_argument(
        "--fact-check",
        choices=["off", "soft", "strict"],
        default=None,
        help=(
            "Fact-check mode after polish. ``soft`` (default) appends "
            "an ``## Unresolved references`` block to the polished "
            "file; ``strict`` raises on findings; ``off`` disables. "
            "Overridden by ATTUNE_AUTHOR_FACT_CHECK if set."
        ),
    )
    fact_check_group.add_argument(
        "--no-fact-check",
        action="store_true",
        help="Shortcut for ``--fact-check=off``.",
    )

    _add_auth_mode_flag(p_gen)

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
    # --- batch-mode flags (mutually exclusive) -----------------------------
    # Sub-group enforces "exactly one of these (or none) at a time" so the
    # user can't ask the CLI to both submit and resume in one invocation.
    batch_group = p_regen.add_mutually_exclusive_group()
    batch_group.add_argument(
        "--batch",
        action="store_true",
        help=(
            "Submit polish requests as one Anthropic batch (~50%% cost). "
            "Detaches; run --resume later to splice results."
        ),
    )
    batch_group.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previously submitted batch and write its templates.",
    )
    batch_group.add_argument(
        "--status",
        action="store_true",
        help="One-shot status of the pending batch. No polling.",
    )
    batch_group.add_argument(
        "--cancel",
        action="store_true",
        help="Cancel the pending batch and remove its state file.",
    )
    p_regen.add_argument(
        "--force",
        action="store_true",
        help=(
            "With --batch: overwrite an existing pending state file "
            "(cancels the previous batch from the local view; the "
            "still-running Anthropic batch is left to finish on its own)."
        ),
    )
    p_regen.add_argument(
        "--json",
        action="store_true",
        help="With --status: emit JSON instead of human-readable output.",
    )
    # Same fact-check controls as p_gen; see that block for design notes.
    regen_fact_check_group = p_regen.add_mutually_exclusive_group()
    regen_fact_check_group.add_argument(
        "--fact-check",
        choices=["off", "soft", "strict"],
        default=None,
        help=(
            "Fact-check mode after polish. ``soft`` (default) appends "
            "an ``## Unresolved references`` block to each polished "
            "file; ``strict`` raises on findings; ``off`` disables. "
            "Overridden by ATTUNE_AUTHOR_FACT_CHECK if set."
        ),
    )
    regen_fact_check_group.add_argument(
        "--no-fact-check",
        action="store_true",
        help="Shortcut for ``--fact-check=off``.",
    )

    _add_auth_mode_flag(p_regen)

    p_cache = sub.add_parser(
        "cache",
        help="Manage the on-disk polish cache",
        description=(
            "Inspect and clear the on-disk LLM polish cache used by the "
            "generator. Entries are pruned automatically by mtime (default "
            "TTL 30 days, configurable via ATTUNE_AUTHOR_POLISH_CACHE_TTL_SECONDS); "
            "this command exposes a manual nuke."
        ),
    )
    cache_sub = p_cache.add_subparsers(dest="cache_command", help="Cache subcommands")
    cache_sub.add_parser(
        "clear",
        help="Delete every cached polish entry",
        description=(
            "Remove all entries from the polish cache directory. Useful "
            "after a prompt change in attune-author itself, or to reclaim "
            "disk space without waiting for the TTL sweep."
        ),
    )

    p_auth = sub.add_parser(
        "auth",
        help="Authentication diagnostics",
        description=(
            "Inspect how attune-author authenticates LLM calls. "
            "'status' reports which auth mode a call would use right "
            "now (Claude subscription via the Agent SDK, or "
            "ANTHROPIC_API_KEY via the Anthropic SDK)."
        ),
    )
    auth_sub = p_auth.add_subparsers(dest="auth_command", help="Auth subcommands")
    auth_sub.add_parser(
        "status",
        help="Report the auth mode a call would use right now",
    )

    p_edit = sub.add_parser(
        "edit",
        help="Open a template in the browser editor",
        description=(
            "Open a template file in the attune-gui editor. Ensures a "
            "local sidecar is running (spawning one if needed), resolves "
            "the path to its registered corpus, and opens the editor in "
            "your default browser."
        ),
    )
    p_edit.add_argument("path", help="Template file to open.")
    p_edit.add_argument(
        "--corpus",
        default=None,
        help="Force a specific registered corpus id instead of auto-resolving.",
    )
    p_edit.add_argument(
        "--no-open",
        action="store_true",
        help="Print the editor URL without launching a browser.",
    )
    p_edit.add_argument(
        "--port",
        type=int,
        default=None,
        help="Sidecar port (default: discover via portfile, else auto-pick).",
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

    p_skills = sub.add_parser(
        "export-skills",
        help="Export an attune-help corpus as Claude Code skill bundles",
        description=(
            "Walk an attune-help-compatible templates/ directory and write "
            "one Claude Code SKILL.md per concept template. Each output "
            "directory becomes a loadable skill: SKILL.md frontmatter "
            "carries the name and description (sourced from "
            "summaries.json) and the body is the concept template."
        ),
    )
    p_skills.add_argument(
        "--source",
        default=None,
        help=(
            "Path to a templates/ directory (must contain concepts/ and "
            "summaries.json). Defaults to attune-help's bundled corpus."
        ),
    )
    p_skills.add_argument(
        "--output",
        default="./skills",
        help="Directory to write SKILL.md files into (default: %(default)s).",
    )
    p_skills.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace any existing SKILL.md instead of skipping it.",
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
        "maintenance-report": _cmd_maintenance_report,
        "generate": _cmd_generate,
        "regenerate": _cmd_regenerate,
        "docs": _cmd_docs,
        "cache": _cmd_cache,
        "auth": _cmd_auth,
        "edit": _cmd_edit,
        "export-skills": _cmd_export_skills,
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
    print(
        "Edit .help/features.yaml to refine, then run: attune-author generate <feature>"
    )

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


def _cmd_maintenance_report(args: argparse.Namespace) -> int:
    """Handle the maintenance-report command (spec task 1.5)."""
    from attune_author.maintenance_contract import (
        format_maintenance_report,
        scan_maintenance,
    )

    help_dir = validate_file_path(args.help_dir)
    templates_dir = help_dir / "templates"
    pages = scan_maintenance([templates_dir])
    print(
        format_maintenance_report(
            pages, base=help_dir, show_auto=getattr(args, "all", False)
        )
    )
    return 0


def _add_auth_mode_flag(parser: argparse.ArgumentParser) -> None:
    """Attach the shared ``--auth-mode`` flag (sibling-subscription-auth).

    Defined once so ``generate`` and ``regenerate`` stay in sync.
    """
    parser.add_argument(
        "--auth-mode",
        choices=["auto", "api", "sub"],
        default=None,
        help=(
            "LLM auth routing for polish calls: 'auto' (default) prefers "
            "the Claude subscription when running under Claude Code and "
            "falls back to ANTHROPIC_API_KEY; 'api' forces the API key; "
            "'sub' forces subscription. Overridden by "
            "ATTUNE_AUTHOR_AUTH_MODE if set. Batch mode (--batch) always "
            "uses the API."
        ),
    )


def _apply_auth_mode_args(args: argparse.Namespace) -> None:
    """Translate ``--auth-mode`` to the env var read by
    :mod:`attune_author.auth`.

    Mirrors :func:`_apply_fact_check_args`: the env var is the single
    source of truth; an already-set env var wins (the operator's
    shell-level intent overrides the per-invocation flag).
    """
    from attune_author.auth import AUTH_MODE_ENV

    if os.environ.get(AUTH_MODE_ENV):
        return
    if getattr(args, "auth_mode", None):
        os.environ[AUTH_MODE_ENV] = args.auth_mode


def _cmd_auth(args: argparse.Namespace) -> int:
    """Handle the auth command (``status``)."""
    from attune_author.auth import AUTH_MODE_ENV, auth_status

    status = auth_status()

    def _yn(value: object) -> str:
        return "yes" if value else "no"

    print("Auth status (attune-author)")
    print(f"  Claude Code session (CLAUDECODE=1): {_yn(status['claudecode'])}")
    print(f"  claude-agent-sdk importable:        {_yn(status['sdk_importable'])}")
    print(f"  ANTHROPIC_API_KEY set:              {_yn(status['api_key_available'])}")
    print(f"  {AUTH_MODE_ENV}:             {status['env_mode'] or '(unset; auto)'}")
    if status["error"]:
        print(f"  Resolved mode: ERROR — {status['error']}", file=sys.stderr)
        return 1
    if status["resolved_mode"] == "sub":
        print("  Resolved mode: subscription (Agent SDK)")
    else:
        print("  Resolved mode: API key (Anthropic SDK)")
        if not status["api_key_available"]:
            print(
                "  WARNING: ANTHROPIC_API_KEY is not set — LLM calls will "
                "fail.\n           Run inside Claude Code for subscription "
                "routing, or set ANTHROPIC_API_KEY."
            )
    return 0


def _apply_fact_check_args(args: argparse.Namespace) -> None:
    """Translate ``--fact-check`` / ``--no-fact-check`` to the env var
    read by :func:`attune_author.generator._run_fact_check`.

    The env var is the single source of truth; the CLI flags are a
    convenience that maps onto it. An already-set env var wins (the
    operator's shell-level intent overrides the per-invocation flag).
    """
    if os.environ.get("ATTUNE_AUTHOR_FACT_CHECK"):
        return
    if getattr(args, "no_fact_check", False):
        os.environ["ATTUNE_AUTHOR_FACT_CHECK"] = "off"
    elif getattr(args, "fact_check", None):
        os.environ["ATTUNE_AUTHOR_FACT_CHECK"] = args.fact_check


def _cmd_generate(args: argparse.Namespace) -> int:
    """Handle the generate command."""
    from attune_author.generator import generate_feature_templates
    from attune_author.manifest import load_manifest

    _apply_fact_check_args(args)
    _apply_auth_mode_args(args)
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
    _apply_fact_check_args(args)
    _apply_auth_mode_args(args)
    root = validate_file_path(args.project_root)
    help_dir = validate_file_path(args.help_dir)

    if getattr(args, "batch", False):
        return _cmd_regenerate_batch_submit(args, help_dir, root)
    if getattr(args, "resume", False):
        return _cmd_regenerate_batch_resume(args, help_dir, root)
    if getattr(args, "status", False):
        return _cmd_regenerate_batch_status(args, help_dir)
    if getattr(args, "cancel", False):
        return _cmd_regenerate_batch_cancel(args, help_dir)

    return _cmd_regenerate_synchronous(args, help_dir, root)


def _cmd_regenerate_synchronous(
    args: argparse.Namespace,
    help_dir: Path,
    root: Path,
) -> int:
    """Default synchronous path. Also surfaces the pending-batch hint."""
    from attune_author.maintenance import run_maintenance
    from attune_author.maintenance_batch import has_pending_batch

    if has_pending_batch(help_dir):
        print(
            "note: a pending batch was previously submitted from this corpus.\n"
            "      run `attune-author regenerate --resume`  to splice its results,\n"
            "      or  `attune-author regenerate --status`  to see progress.",
            file=sys.stderr,
        )

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


def _cmd_regenerate_batch_submit(
    args: argparse.Namespace,
    help_dir: Path,
    root: Path,
) -> int:
    from attune_author.maintenance_batch import (
        BatchAlreadyPending,
        submit_maintenance_batch,
    )

    try:
        state = submit_maintenance_batch(
            help_dir=help_dir,
            project_root=root,
            force=args.force,
        )
    except BatchAlreadyPending as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        _print_missing_manifest_hint(help_dir)
        return 1
    except ValueError as exc:
        # No stale features / nothing to do — surface gracefully.
        print(f"note: {exc}")
        return 0

    print(
        f"Submitted batch {state.batch_id} ({len(state.requests)} requests, model {state.model}).\n"
        f"Estimated completion: ~{_format_eta(state)} (Anthropic 24h SLA)."
    )
    print()
    print("Run  attune-author regenerate --resume   to splice results when ready.")
    return 0


def _cmd_regenerate_batch_resume(
    args: argparse.Namespace,
    help_dir: Path,
    root: Path,
) -> int:
    from attune_author.maintenance_batch import (
        BatchStateExpired,
        BatchStateNotFound,
        resume_maintenance_batch,
    )

    _ = args
    try:
        outcome = resume_maintenance_batch(
            help_dir=help_dir,
            project_root=root,
        )
    except BatchStateNotFound:
        print("no pending batch found. Nothing to resume.", file=sys.stderr)
        return 1
    except BatchStateExpired as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if outcome.final_status == "timed_out":
        print(
            f"Batch {outcome.batch_id} still running. State file kept; run "
            "`attune-author regenerate --resume` again later."
        )
    else:
        print(
            f"Batch {outcome.batch_id} {outcome.final_status}. "
            f"Regenerated {outcome.regenerated_count} feature(s)."
        )
        if outcome.failed:
            print(f"Failed: {', '.join(outcome.failed)}")
    return 0


def _cmd_regenerate_batch_status(
    args: argparse.Namespace,
    help_dir: Path,
) -> int:
    from attune_author.maintenance_batch import (
        BatchStateExpired,
        BatchStateNotFound,
        status_maintenance_batch,
    )

    try:
        info = status_maintenance_batch(help_dir=help_dir)
    except BatchStateNotFound:
        print("no pending batch.", file=sys.stderr)
        return 1
    except BatchStateExpired as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        import json as _json

        print(_json.dumps(info, indent=2, sort_keys=True))
        return 0

    print("Pending batch:")
    print(f"  id:                    {info['batch_id']}")
    print(f"  submitted:             {info['submitted_at']}")
    print(f"  expected completion:   {info['expected_completion_at']}")
    print(f"  model:                 {info['model']}")
    print(f"  request count:         {info['request_count']}")
    print(f"  state (Anthropic):     {info.get('processing_status')}")
    rc = info.get("request_counts") or {}
    if rc:
        print(
            f"  succeeded={rc.get('succeeded', 0)}  "
            f"errored={rc.get('errored', 0)}  "
            f"expired={rc.get('expired', 0)}  "
            f"canceled={rc.get('canceled', 0)}  "
            f"processing={rc.get('processing', 0)}"
        )
    return 0


def _cmd_regenerate_batch_cancel(
    args: argparse.Namespace,
    help_dir: Path,
) -> int:
    from attune_author.maintenance_batch import (
        BatchStateExpired,
        BatchStateNotFound,
        cancel_maintenance_batch,
    )

    _ = args
    try:
        batch_id = cancel_maintenance_batch(help_dir=help_dir)
    except BatchStateNotFound:
        print("no pending batch to cancel.", file=sys.stderr)
        return 1
    except BatchStateExpired as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Canceled batch {batch_id}.")
    return 0


def _format_eta(state: object) -> str:
    """Human-readable ETA for a batch state."""
    submitted = getattr(state, "submitted_at")
    eta = getattr(state, "expected_completion_at")
    delta = eta - submitted
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "<1 min"
    return f"{minutes} min"


def _cmd_cache(args: argparse.Namespace) -> int:
    """Handle the cache command and its subcommands."""
    from attune_author.polish import _cache_dir, clear_cache

    if args.cache_command == "clear":
        deleted = clear_cache()
        cache_path = _cache_dir()
        print(f"Cleared {deleted} entries from {cache_path}")
        return 0

    print("Usage: attune-author cache clear", file=sys.stderr)
    return 1


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


def _cmd_edit(args: argparse.Namespace) -> int:
    """Handle the ``edit`` command — open a template in the browser editor.

    Returns:
        - ``0`` on success.
        - ``1`` if the path doesn't exist or isn't covered by a registered
          corpus and the user declines to register one.
        - ``2`` if the sidecar can't be started.
    """
    abs_path = Path(args.path).expanduser().resolve()
    if not abs_path.exists():
        print(
            f"Path does not exist: {abs_path}\n"
            f"  Hint: pass an absolute or working-dir-relative path to a "
            f"template file.",
            file=sys.stderr,
        )
        return 1

    try:
        sidecar = ensure_sidecar(port=args.port)
    except SidecarStartError as exc:
        print(
            f"Could not start the editor sidecar ({exc.reason}): {exc}", file=sys.stderr
        )
        if exc.reason == "missing_command":
            print("  Install with: pip install attune-gui", file=sys.stderr)
        elif exc.reason == "timeout":
            print(
                "  The configured port may be in use. Try `--port <n>` "
                "with a different port, or stop the conflicting process.",
                file=sys.stderr,
            )
        return 2

    if args.corpus:
        corpus_id = args.corpus
        try:
            rel_path = abs_path.relative_to(_corpus_root(sidecar, corpus_id))
        except ValueError:
            print(
                f"Path {abs_path} is not inside corpus {corpus_id!r}.",
                file=sys.stderr,
            )
            return 1
        rel = rel_path.as_posix()
    else:
        resolved = _resolve_path(sidecar, abs_path)
        if resolved is None:
            return _handle_unregistered_path(sidecar, abs_path)
        corpus_id, rel = resolved

    url = (
        f"{sidecar.url}/editor"
        f"?corpus={urllib.parse.quote(corpus_id)}"
        f"&path={urllib.parse.quote(rel)}"
    )
    print(url)

    if not args.no_open:
        webbrowser.open(url)

    return 0


def _resolve_path(sidecar: PortfileData, abs_path: Path) -> tuple[str, str] | None:
    """POST /api/corpus/resolve. Returns ``(corpus_id, rel_path)`` or None."""
    payload = json.dumps({"abs_path": str(abs_path)}).encode("utf-8")
    req = urllib.request.Request(
        f"{sidecar.url}/api/corpus/resolve",
        data=payload,
        headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    return body["corpus_id"], body["rel_path"]


def _corpus_root(sidecar: PortfileData, corpus_id: str) -> Path:
    """GET /api/corpus → look up the registered root for ``corpus_id``."""
    req = urllib.request.Request(
        f"{sidecar.url}/api/corpus",
        headers={"Origin": "http://127.0.0.1"},
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:  # noqa: S310
        body = json.loads(resp.read().decode("utf-8"))
    for entry in body.get("corpora", []):
        if entry.get("id") == corpus_id:
            return Path(entry["path"])
    raise FileNotFoundError(f"Unknown corpus id: {corpus_id!r}")


def _handle_unregistered_path(sidecar: PortfileData, abs_path: Path) -> int:
    """Path is outside every registered corpus. Prompt to register the parent."""
    parent = abs_path.parent
    print(
        f"{abs_path} is not inside any registered corpus.",
        file=sys.stderr,
    )
    if not sys.stdin.isatty():
        print(
            f"  Register one with the dashboard, or run again interactively. "
            f"Suggested root: {parent}",
            file=sys.stderr,
        )
        return 1
    answer = input(f"Register {parent} as a new corpus? [y/N] ").strip().lower()
    if answer != "y":
        return 1
    return _register_and_retry(sidecar, abs_path, parent)


def _register_and_retry(sidecar: PortfileData, abs_path: Path, root: Path) -> int:
    """POST /api/corpus/register, then retry the open flow."""
    payload = json.dumps(
        {"name": root.name, "path": str(root), "kind": "ad-hoc"}
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{sidecar.url}/api/corpus/register",
        data=payload,
        headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:  # noqa: S310
        entry = json.loads(resp.read().decode("utf-8"))

    corpus_id = entry["id"]
    rel = abs_path.relative_to(root).as_posix()
    url = (
        f"{sidecar.url}/editor"
        f"?corpus={urllib.parse.quote(corpus_id)}"
        f"&path={urllib.parse.quote(rel)}"
    )
    print(url)
    webbrowser.open(url)
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
    print(
        "  Generates concept/task/reference templates for a feature.", file=sys.stderr
    )

    try:
        from attune_author.manifest import load_manifest

        manifest = load_manifest(help_dir)
    except Exception:  # noqa: BLE001
        print(
            f"\nNo manifest found at {help_dir / 'features.yaml'}. Run `attune-author init` first.",
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


def _cmd_export_skills(args: argparse.Namespace) -> int:
    """Handle the ``export-skills`` command.

    Resolves ``--source`` (defaulting to attune-help's bundled
    templates dir via the rag adapter), runs :func:`export_skills`,
    and prints a written/skipped summary.

    Returns:
        ``0`` on success — even when some features were skipped.
        ``1`` if the source directory can't be resolved or doesn't
        contain a ``concepts/`` subtree.
    """
    from attune_author.skill_export import export_skills

    source: Path
    if args.source:
        source = Path(args.source).expanduser().resolve()
    else:
        try:
            from attune_help.adapters.rag import AttuneHelpAdapter
        except ImportError:
            print(
                "Could not import attune_help; pass --source <templates-dir> "
                "or install attune-help.",
                file=sys.stderr,
            )
            return 1
        source = AttuneHelpAdapter().templates_root

    if not (source / "concepts").is_dir():
        print(
            f"Source has no concepts/ subdirectory: {source}\n"
            f"  Hint: pass a templates/ root, not the project or .help/ dir.",
            file=sys.stderr,
        )
        return 1

    output = Path(args.output).expanduser().resolve()
    result = export_skills(source, output, overwrite=args.overwrite)

    print(f"Exported {len(result.written)} skill(s) to {output}")
    for record in result.written:
        print(f"  + {record.feature:<32} {record.body_chars} chars")
    if result.skipped:
        print(f"\nSkipped {len(result.skipped)}:")
        for feature, reason in result.skipped:
            print(f"  - {feature:<32} {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
