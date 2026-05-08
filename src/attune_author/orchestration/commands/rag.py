"""``rag.*`` orchestration commands.

Phase D1 of the architecture-realignment spec. This module owns the
``rag.corpus-info`` command that previously lived inline in
``attune_gui.commands``. Importing the module calls
:func:`attune_author.orchestration.register` so the spec joins the
runtime registry.

The executor builds its own :class:`attune_rag.RagPipeline` from a
``project_path`` arg rather than reaching back into attune-gui's
private ``_get_pipeline`` cache. That keeps the dependency edge
running rag → author (via the optional ``[rag]`` extra) and inverts
nothing. attune-gui's own pipeline cache is unchanged; running the
command from a route just builds a separate pipeline for the
inspection. Phase D4's ``pipeline_for(corpus_id)`` helper will
consolidate the shared cache if that ever matters.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from attune_author.orchestration.context import JobContext
from attune_author.orchestration.exceptions import ValidationError
from attune_author.orchestration.registry import CommandSpec, register


def _build_pipeline(project_path: str | None):
    """Construct an :class:`attune_rag.RagPipeline` for ``project_path``.

    When ``project_path`` resolves to a directory containing
    ``.help/templates/``, that directory is loaded as a
    :class:`attune_rag.DirectoryCorpus`. Otherwise the pipeline is
    built without a corpus and falls back to attune-rag's bundled
    default at retrieval time.

    Lazy-imports :mod:`attune_rag` so importing this module doesn't
    require the optional ``[rag]`` extra; the command surfaces a
    clear ``ValidationError`` if the dep is missing.
    """

    try:
        from attune_rag import DirectoryCorpus, QueryExpander, RagPipeline
    except ImportError as exc:  # pragma: no cover - exercised via integration
        raise ValidationError(
            "attune-rag is not installed; install attune-author[rag] to "
            "use the rag.corpus-info command."
        ) from exc

    corpus = None
    if project_path:
        templates_dir = Path(project_path).expanduser().resolve() / ".help" / "templates"
        if templates_dir.is_dir():
            corpus = DirectoryCorpus(templates_dir)

    return RagPipeline(corpus=corpus, expander=QueryExpander())


async def _exec_rag_corpus_info(args: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
    project_path_raw = str(args.get("project_path", "")).strip() or None
    pipeline = _build_pipeline(project_path_raw)

    entries = await asyncio.to_thread(list, pipeline.corpus.entries())
    kinds = sorted({e.path.split("/")[0] for e in entries if "/" in e.path})
    ctx.log(f"{len(entries)} entries across {len(kinds)} kind(s)")
    return {
        "corpus_class": type(pipeline.corpus).__name__,
        "entry_count": len(entries),
        "kinds": kinds,
    }


_SPEC = CommandSpec(
    name="rag.corpus-info",
    title="Corpus info",
    domain="rag",
    description="Show entry count and category breakdown for the loaded attune-rag corpus.",
    args_schema={
        "type": "object",
        "properties": {
            "project_path": {
                "type": "string",
                "title": "Project path",
                "default": "",
                "description": (
                    "Root of the project whose corpus to inspect. "
                    "Leave blank to use the bundled corpus."
                ),
                "ui:widget": "path",
                "ui:browseHint": "project",
            },
        },
    },
    executor=_exec_rag_corpus_info,
    cancellable=False,
    profiles=("developer", "author"),
)


register(_SPEC)
