"""Help maintenance logic for commit hooks and manual refresh.

Ties together manifest, staleness, and generator modules to
detect which features need help updates and regenerate their
templates.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from attune_author.generator import GenerationResult, generate_feature_templates
from attune_author.manifest import load_manifest, match_files_to_features
from attune_author.staleness import StalenessReport, check_staleness

logger = logging.getLogger(__name__)


@dataclass
class MaintenanceResult:
    """Result of a help maintenance run.

    Attributes:
        staleness: Full staleness report.
        regenerated: Features whose templates were regenerated.
        skipped_manual: Features skipped (status: manual).
        failed: Features that failed to regenerate.
    """

    staleness: StalenessReport
    regenerated: list[GenerationResult] = field(default_factory=list)
    skipped_manual: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    @property
    def stale_count(self) -> int:
        """Number of stale features detected."""
        return self.staleness.stale_count

    @property
    def regenerated_count(self) -> int:
        """Number of features regenerated."""
        return len(self.regenerated)


def _resolve_stale_features(
    help_dir: str | Path,
    project_root: str | Path,
    features: list[str] | None = None,
) -> list:
    """Return a list of stale ``Feature`` objects.

    Used by both the synchronous path and the batch path so they
    pick up the exact same set of features to regenerate. Returns
    an empty list when nothing is stale.
    """
    manifest = load_manifest(help_dir)
    report = check_staleness(manifest, help_dir, project_root, features)
    out = []
    for entry in report.help_entries:
        if not entry.is_stale:
            continue
        feat = manifest.features.get(entry.feature)
        if feat is None:
            continue
        out.append(feat)
    return out


def run_maintenance(
    help_dir: str | Path,
    project_root: str | Path,
    features: list[str] | None = None,
    dry_run: bool = False,
) -> MaintenanceResult:
    """Run help maintenance — check staleness and regenerate.

    Args:
        help_dir: Path to the .help/ directory.
        project_root: Project root for resolving globs.
        features: Optional list of feature names to check.
            If None, checks all features.
        dry_run: If True, report staleness without regenerating.

    Returns:
        MaintenanceResult with staleness and regeneration info.

    Raises:
        FileNotFoundError: If features.yaml doesn't exist.
    """
    manifest = load_manifest(help_dir)
    report = check_staleness(manifest, help_dir, project_root, features)

    result = MaintenanceResult(staleness=report)

    if dry_run or report.stale_count == 0:
        return result

    # Reset Phase 3 faithfulness telemetry so the end-of-run summary
    # reflects this regen rather than carrying state across runs.
    from attune_author.generator import reset_faithfulness_telemetry
    from attune_author.polish import reset_polish_cache_telemetry

    reset_faithfulness_telemetry()
    reset_polish_cache_telemetry()

    for entry in report.help_entries:
        if not entry.is_stale:
            continue

        feat = manifest.features.get(entry.feature)
        if not feat:
            continue

        try:
            gen_result = generate_feature_templates(
                feature=feat,
                help_dir=help_dir,
                project_root=project_root,
            )
            result.regenerated.append(gen_result)
            logger.info(
                "Regenerated %d templates for '%s'",
                len(gen_result.templates),
                entry.feature,
            )
        except OSError as e:
            logger.error(
                "Failed to regenerate '%s': %s",
                entry.feature,
                e,
            )
            result.failed.append(entry.feature)

    # Phase 3 telemetry summary. Logged at INFO so it appears in the
    # default `attune-author regenerate` output. Silent when the judge
    # didn't run at all (disabled or never reached).
    from attune_author.generator import _faithfulness_telemetry

    telemetry = _faithfulness_telemetry()
    if telemetry["calls"] or telemetry["skipped"]:
        logger.info(
            "Faithfulness judge: %d call(s), %d skipped, estimated cost $%.4f",
            int(telemetry["calls"]),
            int(telemetry["skipped"]),
            telemetry["cost_usd"],
        )

    # Prompt-cache hit-rate summary. Logged at INFO so it rides the
    # same default `attune-author regenerate` output as the
    # faithfulness line; silent when polish never ran this regen.
    from attune_author.polish import format_polish_cache_summary

    cache_summary = format_polish_cache_summary()
    if cache_summary is not None:
        logger.info("%s", cache_summary)

    return result


def get_changed_files(project_root: str | Path) -> list[str]:
    """Get files changed in the most recent commit.

    Uses git diff to find changed files. Returns relative
    paths from the project root.

    Args:
        project_root: Project root directory.

    Returns:
        List of relative file paths changed in HEAD.
    """
    try:
        output = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if output.returncode != 0:
            logger.debug("git diff failed: %s", output.stderr)
            return []
        return [line.strip() for line in output.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.debug("Cannot get changed files: %s", e)
        return []


def run_hook(
    help_dir: str | Path,
    project_root: str | Path,
) -> MaintenanceResult | None:
    """Post-commit hook entry point.

    Gets changed files from the latest commit, matches them
    against the feature manifest, and regenerates templates
    for affected features only.

    Args:
        help_dir: Path to the .help/ directory.
        project_root: Project root directory.

    Returns:
        MaintenanceResult if any features were affected,
        None if the manifest doesn't exist or no features
        matched.
    """
    help_path = Path(help_dir)
    if not (help_path / "features.yaml").exists():
        return None

    changed = get_changed_files(project_root)
    if not changed:
        return None

    try:
        manifest = load_manifest(help_dir)
    except (FileNotFoundError, ValueError) as e:
        logger.warning("Cannot load manifest: %s", e)
        return None

    affected = match_files_to_features(changed, manifest)
    if not affected:
        return None

    affected_names = list(affected.keys())
    logger.info(
        "Commit touches %d feature(s): %s",
        len(affected_names),
        ", ".join(affected_names),
    )

    return run_maintenance(
        help_dir=help_dir,
        project_root=project_root,
        features=affected_names,
    )


def format_status_report(
    report: StalenessReport,
    help_dir: str | Path | None = None,
) -> str:
    """Format a staleness report for display.

    Renders two sections:
    - **Help Templates** — ``.help/`` template staleness by feature.
    - **Project Docs** — ``docs/`` file staleness (missing or hash
      mismatch). Only shown when the manifest has ``doc_path`` /
      ``arch_path`` entries.

    Args:
        report: The staleness report to format.
        help_dir: Path to .help/ directory for preamble lookup.

    Returns:
        Markdown-formatted status report.
    """
    from attune_author.preamble import get_preamble

    help_stale = sum(1 for e in report.help_entries if e.is_stale)
    help_current = sum(1 for e in report.help_entries if not e.is_stale)

    lines = ["## Help Templates\n"]
    lines.append(f"**{help_current}** current, **{help_stale}** stale\n")

    if help_stale > 0:
        lines.append("### Stale\n")
        lines.append("| Feature | Description | Files Changed |\n")
        lines.append("|---------|-------------|---------------|\n")
        for entry in report.help_entries:
            if entry.is_stale:
                count = len(entry.matched_files)
                preamble = get_preamble(entry.feature, help_dir) or ""
                lines.append(f"| {entry.feature} | {preamble} | {count} source files |\n")
        lines.append("")

    if help_current > 0:
        lines.append("### Current\n")
        for entry in report.help_entries:
            if not entry.is_stale:
                preamble = get_preamble(entry.feature, help_dir) or ""
                if preamble:
                    lines.append(f"- **{entry.feature}** — {preamble}\n")
                else:
                    lines.append(f"- {entry.feature}\n")
        lines.append("")

    # --- Project Docs section (only shown when doc entries exist) ---
    if report.doc_entries:
        doc_stale = sum(1 for d in report.doc_entries if d.is_stale)
        doc_current = sum(1 for d in report.doc_entries if not d.is_stale)

        lines.append("## Project Docs\n")
        lines.append(f"**{doc_current}** current, **{doc_stale}** stale\n")

        if doc_stale > 0:
            lines.append("### Stale\n")
            lines.append("| Feature | Path | Kind | Status |\n")
            lines.append("|---------|------|------|--------|\n")
            for doc in report.doc_entries:
                if doc.is_stale:
                    status = "missing" if doc.missing else "hash mismatch"
                    lines.append(f"| {doc.feature} | {doc.doc_path} | {doc.kind} | {status} |\n")
            lines.append("")

        if doc_current > 0:
            lines.append("### Current\n")
            for doc in report.doc_entries:
                if not doc.is_stale:
                    lines.append(f"- **{doc.feature}** `{doc.doc_path}` ({doc.kind})\n")
            lines.append("")

    return "\n".join(lines)
