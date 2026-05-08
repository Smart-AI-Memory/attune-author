"""``author.*`` orchestration commands.

Phase D2 of the architecture-realignment spec. Owns all six
``author.*`` executors that previously lived inline in
``attune_gui.commands``: ``init``, ``status``, ``maintain``,
``lookup``, ``regen``, ``setup``. Importing this module registers
each spec on the orchestration registry.

Two side effects in the original gui code don't move with the
executor:

- ``_resolve_project_paths`` previously fell back to
  ``attune_gui.workspace.get_workspace()`` when no path was given.
  Workspace knowledge belongs to the host (gui), not the
  orchestration runtime; hosts must supply paths explicitly. The
  gui's proxy dispatcher fills them in from the workspace before
  calling :func:`run_command`.
- ``author.regen`` and ``author.setup`` previously called
  ``attune_gui.routes.rag.invalidate(project_root)`` to bust the
  gui's pipeline cache. That's a host concern; the gui's specialized
  proxy invalidates after dispatch instead.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from attune_author.orchestration._helpers import resolve_project_paths
from attune_author.orchestration.context import JobContext
from attune_author.orchestration.exceptions import ValidationError
from attune_author.orchestration.registry import CommandSpec, register

# ---------------------------------------------------------------------------
# author.init
# ---------------------------------------------------------------------------


async def _exec_init(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    from attune_author.bootstrap import proposals_to_manifest, scan_project
    from attune_author.manifest import save_manifest

    project_root = Path(args.get("project_root", ".")).resolve()
    help_dir = project_root / ".help"

    if (help_dir / "features.yaml").exists():
        ctx.log("Already initialised — skipping scan")
        return {
            "already_initialized": True,
            "manifest_path": str(help_dir / "features.yaml"),
        }

    ctx.log(f"Scanning {project_root} for features…")
    proposals = await asyncio.to_thread(scan_project, project_root)
    ctx.log(f"Discovered {len(proposals)} feature(s)")

    if not proposals:
        return {"discovered": 0, "message": "No features discovered in project."}

    manifest = proposals_to_manifest(proposals)
    manifest_path = await asyncio.to_thread(save_manifest, manifest, help_dir)
    ctx.log(f"Wrote manifest to {manifest_path}")

    return {
        "discovered": len(proposals),
        "manifest_path": str(manifest_path),
        "features": [{"name": p.name, "description": p.description} for p in proposals],
    }


_SPEC_INIT = CommandSpec(
    name="author.init",
    title="Init .help/",
    domain="author",
    description="Scan the project and bootstrap a .help/features.yaml manifest.",
    args_schema={
        "type": "object",
        "properties": {
            "project_root": {
                "type": "string",
                "title": "Project root",
                "default": ".",
                "description": "Root of the project to scan.",
                "ui:widget": "path",
                "ui:browseHint": "project",
            },
        },
    },
    executor=_exec_init,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# author.status
# ---------------------------------------------------------------------------


async def _exec_status(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    from attune_author.maintenance import format_status_report
    from attune_author.manifest import load_manifest
    from attune_author.staleness import check_staleness

    project_root, help_dir = resolve_project_paths(args)

    ctx.log(f"Loading manifest from {help_dir}…")
    manifest = await asyncio.to_thread(load_manifest, help_dir)
    ctx.log(f"Checking staleness for {len(manifest.features)} feature(s)…")
    report = await asyncio.to_thread(check_staleness, manifest, help_dir, project_root, None)
    total = report.stale_count + report.current_count
    ctx.log(f"Stale: {report.stale_count} / {total}")

    return {
        "total": total,
        "stale": report.stale_count,
        "fresh": report.current_count,
        "report": format_status_report(report),
    }


_STATUS_ARGS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_path": {
            "type": "string",
            "title": "Project path",
            "default": "",
            "ui:widget": "path",
            "ui:browseHint": "project",
        },
        "help_dir": {
            "type": "string",
            "title": ".help/ path (overrides project_path)",
            "default": "",
            "ui:widget": "path",
        },
        "project_root": {
            "type": "string",
            "title": "Project root (overrides project_path)",
            "default": "",
            "ui:widget": "path",
            "ui:browseHint": "project",
        },
    },
}


_SPEC_STATUS = CommandSpec(
    name="author.status",
    title="Template status",
    domain="author",
    description="Report which help templates are stale vs. fresh.",
    args_schema=_STATUS_ARGS_SCHEMA,
    executor=_exec_status,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# author.maintain
# ---------------------------------------------------------------------------


async def _exec_maintain(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    """Regenerate stale templates with per-feature progress.

    Mirrors :func:`attune_author.maintenance.run_maintenance` but calls
    ``generate_feature_templates`` one feature at a time so the host
    can stream a log line per feature.
    """
    from attune_author.generator import generate_feature_templates
    from attune_author.maintenance import MaintenanceResult
    from attune_author.manifest import load_manifest
    from attune_author.staleness import check_staleness

    project_root, help_dir = resolve_project_paths(args)
    dry_run = bool(args.get("dry_run", False))
    features_raw = str(args.get("features", "")).strip()
    features = [f.strip() for f in features_raw.split(",") if f.strip()] or None

    label = "Dry-run check" if dry_run else "Regenerating stale templates"
    ctx.log(f"{label} in {help_dir}…")

    manifest = await asyncio.to_thread(load_manifest, help_dir)
    report = await asyncio.to_thread(check_staleness, manifest, help_dir, project_root, features)
    result = MaintenanceResult(staleness=report)

    total = report.stale_count + report.current_count
    ctx.log(f"Stale: {report.stale_count} / {total}")

    if dry_run or report.stale_count == 0:
        return {
            "stale_count": report.stale_count,
            "total_count": total,
            "regenerated": [],
            "failed": [],
            "dry_run": dry_run,
            "project_root": str(project_root),
        }

    stale_entries = [e for e in report.help_entries if e.is_stale]
    n_stale = len(stale_entries)
    for idx, entry in enumerate(stale_entries, start=1):
        feat = manifest.features.get(entry.feature)
        if feat is None:
            ctx.log(f"  [{idx}/{n_stale}] {entry.feature}: not in manifest — skip")
            continue

        try:
            gen = await asyncio.to_thread(
                generate_feature_templates,
                feature=feat,
                help_dir=help_dir,
                project_root=project_root,
            )
            result.regenerated.append(gen)
            ctx.log(f"  [{idx}/{n_stale}] {entry.feature}: {len(gen.templates)} template(s)")
        # INTENTIONAL: per-feature failure must not abort the batch
        except Exception as exc:  # noqa: BLE001
            ctx.log(f"  [{idx}/{n_stale}] {entry.feature}: FAILED — {exc}")
            result.failed.append(entry.feature)

    ctx.log(f"Regenerated: {len(result.regenerated)}, failed: {len(result.failed)}")

    return {
        "stale_count": report.stale_count,
        "total_count": total,
        "regenerated": [r.feature for r in result.regenerated],
        "failed": result.failed,
        "dry_run": dry_run,
        # Surfaced so the host can invalidate any cached pipelines tied to project_root.
        "project_root": str(project_root),
    }


_MAINTAIN_ARGS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        **_STATUS_ARGS_SCHEMA["properties"],
        "features": {
            "type": "string",
            "title": "Features (comma-separated)",
            "default": "",
            "description": "Leave blank to check all features.",
        },
        "dry_run": {"type": "boolean", "title": "Dry run", "default": False},
    },
}


_SPEC_MAINTAIN = CommandSpec(
    name="author.maintain",
    title="Maintain templates",
    domain="author",
    description="Regenerate all stale help templates (or dry-run to preview what would change).",
    args_schema=_MAINTAIN_ARGS_SCHEMA,
    executor=_exec_maintain,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# author.lookup
# ---------------------------------------------------------------------------


async def _exec_lookup(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    from attune_author.manifest import is_safe_feature_name, load_manifest, resolve_topic

    query = args.get("query")
    if not query:
        raise ValidationError("query is required")

    depth = args.get("depth", "concept")
    help_dir = Path(args.get("help_dir", ".help")).resolve()

    ctx.log(f"Looking up {query!r} (depth={depth})…")
    manifest = await asyncio.to_thread(load_manifest, help_dir)
    feature_name = resolve_topic(query, manifest)

    if not feature_name:
        available = sorted(manifest.features)
        raise ValidationError(f"No feature matches {query!r}. Available: {', '.join(available)}")

    if not is_safe_feature_name(feature_name):
        raise ValidationError(f"Invalid feature name: {feature_name!r}")

    template_path = help_dir / "templates" / feature_name / f"{depth}.md"
    if not template_path.exists():
        raise ValidationError(
            f"No {depth} template for '{feature_name}'. Run author.generate first."
        )

    content = template_path.read_text(encoding="utf-8")
    ctx.log(f"Loaded template for '{feature_name}' ({len(content)} chars)")

    return {
        "feature": feature_name,
        "depth": depth,
        "path": str(template_path),
        "content": content,
    }


_SPEC_LOOKUP = CommandSpec(
    name="author.lookup",
    title="Lookup template",
    domain="author",
    description="Read a rendered help template for a feature by name or tag.",
    args_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "title": "Feature / tag",
                "minLength": 1,
                "description": "Feature name or tag to look up.",
            },
            "depth": {
                "type": "string",
                "title": "Depth",
                "default": "concept",
                "description": "concept | task | reference",
            },
            "help_dir": {
                "type": "string",
                "title": ".help/ path",
                "default": ".help",
                "ui:widget": "path",
            },
        },
        "required": ["query"],
    },
    executor=_exec_lookup,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# author.regen
# ---------------------------------------------------------------------------


async def _exec_regen(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    from attune_author.generator import generate_feature_templates
    from attune_author.manifest import load_manifest

    project_root, help_dir = resolve_project_paths(args)
    feature_name = str(args.get("feature", "")).strip()
    overwrite = bool(args.get("overwrite", True))

    ctx.log(f"Loading manifest from {help_dir}…")
    manifest = await asyncio.to_thread(load_manifest, help_dir)

    if feature_name:
        if feature_name not in manifest.features:
            available = ", ".join(sorted(manifest.features)) or "(none)"
            raise ValidationError(
                f"Feature {feature_name!r} not in manifest. Available: {available}"
            )
        targets = [manifest.features[feature_name]]
    else:
        targets = list(manifest.features.values())

    ctx.log(f"Regenerating {len(targets)} feature(s)…")
    generated: list[dict[str, Any]] = []
    failed: list[str] = []
    for feat in targets:
        try:
            result = await asyncio.to_thread(
                generate_feature_templates,
                feature=feat,
                help_dir=help_dir,
                project_root=project_root,
                depths=None,
                overwrite=overwrite,
            )
            ctx.log(f"  {feat.name}: {len(result.templates)} template(s)")
            generated.append({"feature": feat.name, "templates": len(result.templates)})
        # INTENTIONAL: per-feature failure must not abort the batch
        except Exception as exc:  # noqa: BLE001
            ctx.log(f"  {feat.name}: FAILED — {exc}")
            failed.append(feat.name)

    ctx.log(f"Done — {len(generated)} generated, {len(failed)} failed")
    return {
        "generated": generated,
        "failed": failed,
        "project_root": str(project_root),
    }


_SPEC_REGEN = CommandSpec(
    name="author.regen",
    title="Regenerate templates",
    domain="author",
    description="Regenerate help templates for one feature or all features in a project.",
    args_schema={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "title": "Project path",
                "default": "",
                "description": "Root of the project. Leave blank to use the configured workspace.",
                "ui:widget": "path",
                "ui:browseHint": "project",
            },
            "feature": {
                "type": "string",
                "title": "Feature (leave blank for all)",
                "default": "",
                "description": "Feature name from the manifest. Leave blank to regenerate all.",
                "ui:choicesUrl": "/api/author/features?project_path={project_path}",
            },
            "overwrite": {
                "type": "boolean",
                "title": "Overwrite existing templates",
                "default": True,
            },
        },
    },
    executor=_exec_regen,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# author.setup
# ---------------------------------------------------------------------------


async def _exec_setup(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    from attune_author.bootstrap import proposals_to_manifest, scan_project
    from attune_author.generator import generate_feature_templates
    from attune_author.manifest import load_manifest, save_manifest

    project_root, help_dir = resolve_project_paths(args)
    overwrite = bool(args.get("overwrite", False))

    manifest_path = help_dir / "features.yaml"
    if manifest_path.exists():
        ctx.log("Manifest exists — skipping init")
    else:
        ctx.log(f"Scanning {project_root} for features…")
        proposals = await asyncio.to_thread(scan_project, project_root)
        ctx.log(f"Discovered {len(proposals)} feature(s)")
        if not proposals:
            return {"discovered": 0, "message": "No features discovered in project."}
        manifest = proposals_to_manifest(proposals)
        await asyncio.to_thread(save_manifest, manifest, help_dir)
        ctx.log(f"Wrote manifest to {manifest_path}")

    manifest = await asyncio.to_thread(load_manifest, help_dir)
    features = list(manifest.features.values())
    ctx.log(f"Generating templates for {len(features)} feature(s)…")

    generated: list[dict[str, Any]] = []
    failed: list[str] = []
    for feat in features:
        try:
            result = await asyncio.to_thread(
                generate_feature_templates,
                feature=feat,
                help_dir=help_dir,
                project_root=project_root,
                depths=None,
                overwrite=overwrite,
            )
            ctx.log(f"  {feat.name}: {len(result.templates)} template(s)")
            generated.append({"feature": feat.name, "templates": len(result.templates)})
        # INTENTIONAL: per-feature failure must not abort the batch
        except Exception as exc:  # noqa: BLE001
            ctx.log(f"  {feat.name}: FAILED — {exc}")
            failed.append(feat.name)

    ctx.log(f"Done — {len(generated)} generated, {len(failed)} failed")
    return {
        "manifest_path": str(manifest_path),
        "features_total": len(features),
        "generated": generated,
        "failed": failed,
        "project_root": str(project_root),
    }


_SPEC_SETUP = CommandSpec(
    name="author.setup",
    title="Setup help",
    domain="author",
    description=(
        "Init .help/ (if needed) and generate all help templates for a project in one step."
    ),
    args_schema={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "title": "Project path",
                "default": "",
                "description": (
                    "Root of the project to set up help for. "
                    "Leave blank to use the configured workspace."
                ),
                "ui:widget": "path",
                "ui:browseHint": "project",
            },
            "overwrite": {
                "type": "boolean",
                "title": "Overwrite existing templates",
                "default": False,
            },
        },
    },
    executor=_exec_setup,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

for _spec in (
    _SPEC_INIT,
    _SPEC_STATUS,
    _SPEC_MAINTAIN,
    _SPEC_LOOKUP,
    _SPEC_REGEN,
    _SPEC_SETUP,
):
    register(_spec)
