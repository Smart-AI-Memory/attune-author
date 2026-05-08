"""``help.*`` orchestration commands.

Phase D3 of the architecture-realignment spec. Owns the three
``help.*`` executors that previously lived inline in
``attune_gui.commands``: ``lookup``, ``search``, ``list``.
Importing this module registers each spec on the orchestration
registry.

attune-help is **not** a hard dep of attune-author. The executor
imports :class:`attune_help.HelpEngine` lazily inside
:func:`_help_engine` and raises :class:`ValidationError` if
attune-help is missing. Hosts that wire ``help.*`` into a job
runner (currently only attune-gui) already declare attune-help as
a runtime dep, so the lazy import is invisible to them. Adding
attune-help as a hard dep here would create a circular package-
metadata edge with attune-help's transitional shim (which depends
on attune-author until 2026-07-07).
"""

from __future__ import annotations

import asyncio
from typing import Any

from attune_author.orchestration.context import JobContext
from attune_author.orchestration.exceptions import ValidationError
from attune_author.orchestration.registry import CommandSpec, register


def _help_engine(template_dir: str | None, job_id: str):
    from pathlib import Path

    try:
        from attune_help import HelpEngine
    except ImportError as exc:  # pragma: no cover - exercised via integration
        raise ValidationError(
            "attune-help is not installed; install it (or use attune-gui, "
            "which already depends on it) to run help.* commands."
        ) from exc

    return HelpEngine(
        template_dir=Path(template_dir).resolve() if template_dir else None,
        renderer="plain",
        user_id=job_id,
    )


# ---------------------------------------------------------------------------
# help.lookup
# ---------------------------------------------------------------------------


_DEPTH_STEPS = {"concept": 1, "task": 2, "reference": 3}


async def _exec_lookup(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    topic = args.get("topic")
    if not topic:
        raise ValidationError("topic is required")

    depth = args.get("depth", "concept")
    template_dir = args.get("template_dir") or None

    steps = _DEPTH_STEPS.get(depth, 1)
    engine = _help_engine(template_dir, ctx.job_id)
    ctx.log(f"Looking up {topic!r} at depth={depth} ({steps} step(s))…")

    content = None
    for _ in range(steps):
        content = await asyncio.to_thread(engine.lookup, topic, suggest_on_miss=True)

    if content is None:
        raise ValidationError(f"No help found for topic {topic!r}.")

    topics = await asyncio.to_thread(engine.list_topics)
    ctx.log(f"Retrieved from {engine.generated_dir}")
    return {
        "topic": topic,
        "depth": depth,
        "content": content,
        "template_dir": str(engine.generated_dir),
        "total_topics": len(topics),
    }


_LOOKUP_SPEC = CommandSpec(
    name="help.lookup",
    title="Help lookup",
    domain="help",
    description="Look up a help topic with progressive depth (concept → task → reference).",
    args_schema={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "title": "Topic",
                "minLength": 1,
                "description": "Topic slug or feature name to look up.",
            },
            "depth": {
                "type": "string",
                "title": "Depth",
                "default": "concept",
                "description": "concept | task | reference",
            },
            "template_dir": {
                "type": "string",
                "title": "Template dir",
                "default": "",
                "description": (
                    "Path to .help/templates/ directory. Leave blank to use bundled templates."
                ),
                "ui:widget": "path",
            },
        },
        "required": ["topic"],
    },
    executor=_exec_lookup,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# help.search
# ---------------------------------------------------------------------------


async def _exec_search(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    query = args.get("query")
    if not query:
        raise ValidationError("query is required")

    limit = int(args.get("limit", 10))
    template_dir = args.get("template_dir") or None

    engine = _help_engine(template_dir, "search")
    ctx.log(f"Searching {query!r} (limit={limit})…")

    results = await asyncio.to_thread(engine.search, query, limit=limit)
    ctx.log(f"Found {len(results)} result(s)")
    return {
        "query": query,
        "results": results,
        "count": len(results),
        "template_dir": str(engine.generated_dir),
    }


_SEARCH_SPEC = CommandSpec(
    name="help.search",
    title="Help search",
    domain="help",
    description="Fuzzy-search help topics by keyword across the template library.",
    args_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "title": "Query",
                "minLength": 1,
                "description": "Keyword or phrase to search for.",
            },
            "limit": {
                "type": "integer",
                "title": "Limit",
                "default": 10,
                "minimum": 1,
                "maximum": 50,
            },
            "template_dir": {
                "type": "string",
                "title": "Template dir",
                "default": "",
                "description": (
                    "Path to .help/templates/ directory. Leave blank to use bundled templates."
                ),
                "ui:widget": "path",
            },
        },
        "required": ["query"],
    },
    executor=_exec_search,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# help.list
# ---------------------------------------------------------------------------


async def _exec_list(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    type_filter = args.get("type_filter") or None
    template_dir = args.get("template_dir") or None

    engine = _help_engine(template_dir, "list")
    ctx.log(f"Listing topics{f' (type={type_filter})' if type_filter else ''}…")

    topics = await asyncio.to_thread(engine.list_topics, type_filter=type_filter)
    ctx.log(f"{len(topics)} topic(s) found in {engine.generated_dir}")
    return {
        "topics": topics,
        "count": len(topics),
        "type_filter": type_filter,
        "template_dir": str(engine.generated_dir),
    }


_LIST_SPEC = CommandSpec(
    name="help.list",
    title="List topics",
    domain="help",
    description=(
        "List all available help topics, "
        "optionally filtered by type (concepts, tasks, references)."
    ),
    args_schema={
        "type": "object",
        "properties": {
            "type_filter": {
                "type": "string",
                "title": "Type filter",
                "default": "",
                "description": "concepts | tasks | references | (blank for all)",
            },
            "template_dir": {
                "type": "string",
                "title": "Template dir",
                "default": "",
                "description": (
                    "Path to .help/templates/ directory. Leave blank to use bundled templates."
                ),
                "ui:widget": "path",
            },
        },
    },
    executor=_exec_list,
    cancellable=False,
    profiles=("developer", "author"),
)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

for _spec in (_LOOKUP_SPEC, _SEARCH_SPEC, _LIST_SPEC):
    register(_spec)
