"""Generate Claude Code skill bundles from an attune-help template corpus.

Each ``concepts/<feature>.md`` template plus its entry in
``summaries.json`` becomes one Claude Code skill::

    output_dir/
    └── <feature>/
        └── SKILL.md          frontmatter: name, description; body: concept

Skill consumers (Claude Code, the marketplace, anything that reads
SKILL.md) can then load the help corpus as native skills with
their own progressive-disclosure mechanism: SKILL.md is the
description-triggered entry point, and a future PR can layer task /
reference depth files alongside it for `Skill` to load on demand.

This is a build-time export — there's no runtime coupling between
attune-author and Claude Code. The output directory is yours to
ship inside a plugin, commit to a repo, or `attune-help`'s own
distribution.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import frontmatter
import yaml

logger = logging.getLogger(__name__)

#: Slug pattern matching attune-help's ``is_safe_feature_name`` — keeps
#: the export defensive about untrusted input even though templates
#: typically come from a trusted manifest.
_SAFE_SLUG = re.compile(r"^[a-z][a-z0-9-]*$")

#: Concept filenames in attune-help often carry a category prefix
#: (``tool-security-audit.md``, ``task-database-migrations.md``) for
#: in-corpus organisation. The canonical feature slug — the one
#: ``summaries.json`` is keyed by, and the one downstream skill
#: consumers expect — is the bare suffix.
_CATEGORY_PREFIXES: tuple[str, ...] = ("tool-", "task-")


def _canonical_slug(file_stem: str) -> str:
    for prefix in _CATEGORY_PREFIXES:
        if file_stem.startswith(prefix):
            return file_stem[len(prefix) :]
    return file_stem


def _first_paragraph_summary(body: str, max_chars: int = 200) -> str | None:
    """Best-effort one-line description pulled from the body.

    Skips headings and blank lines, joins the first prose paragraph,
    truncates at the first sentence boundary, and caps at ``max_chars``.
    Returns ``None`` if no prose was found.
    """
    lines: list[str] = []
    for raw in body.split("\n"):
        stripped = raw.strip()
        if not stripped:
            if lines:
                break
            continue
        if stripped.startswith("#"):
            continue
        lines.append(stripped)
    if not lines:
        return None
    paragraph = " ".join(lines)
    for delim in (". ", "? ", "! "):
        head, sep, _ = paragraph.partition(delim)
        if sep:
            sentence = head + delim.strip()
            if len(sentence) <= max_chars:
                return sentence
            break
    if len(paragraph) > max_chars:
        return paragraph[: max_chars - 1].rstrip() + "…"
    return paragraph


@dataclass(frozen=True)
class SkillRecord:
    """One generated SKILL.md plus its source provenance."""

    feature: str
    skill_path: Path
    description: str
    body_chars: int


@dataclass
class ExportResult:
    """Outcome of a single :func:`export_skills` call.

    ``skipped`` records features the export couldn't write — missing
    concept template, unsafe slug, malformed frontmatter — paired with
    a one-line reason so a CLI caller can surface a useful summary.
    """

    written: list[SkillRecord] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


def _load_summaries(template_dir: Path) -> dict[str, str]:
    """Return ``{feature_slug: one-line description}`` from summaries.json.

    Missing or malformed file returns an empty dict — the export then
    falls back to a generic description per feature.
    """
    path = template_dir / "summaries.json"
    if not path.exists():
        return {}
    try:
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - corrupted summaries fall back to {}
        logger.warning("could not parse %s; ignoring", path)
        return {}
    if not isinstance(data, dict):
        return {}
    # Normalise to str keys + str values; drop anything else.
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}


def _read_concept(path: Path) -> tuple[dict[str, Any], str] | None:
    """Return ``(frontmatter_dict, body_str)`` or ``None`` on parse failure."""
    try:
        post = frontmatter.load(str(path))
    except Exception:  # noqa: BLE001 - bad frontmatter / encoding falls back to skip
        logger.warning("frontmatter parse failed for %s", path)
        return None
    return dict(post.metadata), post.content


def _build_skill_md(*, feature: str, description: str, body: str) -> str:
    """Compose ``SKILL.md`` text given the inputs the export resolved.

    Uses YAML safe-dump for the frontmatter so titles with quotes /
    colons can't break the SKILL.md format.
    """
    fm = yaml.safe_dump(
        {"name": feature, "description": description},
        sort_keys=False,
        allow_unicode=True,
    ).strip()
    body = body.strip()
    return f"---\n{fm}\n---\n\n{body}\n"


def export_skills(
    template_dir: Path,
    output_dir: Path,
    *,
    overwrite: bool = False,
) -> ExportResult:
    """Write one ``<feature>/SKILL.md`` per concept template under ``output_dir``.

    Args:
        template_dir: Root of an attune-help-compatible corpus
            (typically ``attune_help.adapters.rag.AttuneHelpAdapter().templates_root``,
            or a project's local ``.help/templates/``).
        output_dir: Where to write the skill bundles. Created if missing.
        overwrite: When ``True``, replace existing ``SKILL.md`` files; when
            ``False`` (default), skip any feature whose target file already
            exists and record it under :attr:`ExportResult.skipped`.

    Returns:
        :class:`ExportResult` summarising what was written and what was
        skipped (and why).
    """

    concepts_dir = template_dir / "concepts"
    if not concepts_dir.is_dir():
        logger.warning("no concepts/ under %s; nothing to export", template_dir)
        return ExportResult()

    summaries = _load_summaries(template_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = ExportResult()

    for concept_path in sorted(concepts_dir.glob("*.md")):
        file_stem = concept_path.stem
        if not _SAFE_SLUG.match(file_stem):
            result.skipped.append((file_stem, "unsafe slug"))
            continue

        feature = _canonical_slug(file_stem)
        parsed = _read_concept(concept_path)
        if parsed is None:
            result.skipped.append((feature, "frontmatter parse failed"))
            continue
        meta, body = parsed
        if not body.strip():
            result.skipped.append((feature, "empty concept body"))
            continue

        description = (
            summaries.get(feature)
            or summaries.get(file_stem)
            or _description_from_meta(meta, feature)
            or _first_paragraph_summary(body)
            or f"Help content for the {feature.replace('-', ' ')} topic."
        )
        skill_dir = output_dir / feature
        skill_path = skill_dir / "SKILL.md"

        if skill_path.exists() and not overwrite:
            result.skipped.append((feature, "exists (pass --overwrite to replace)"))
            continue

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            _build_skill_md(feature=feature, description=description, body=body),
            encoding="utf-8",
        )
        result.written.append(
            SkillRecord(
                feature=feature,
                skill_path=skill_path,
                description=description,
                body_chars=len(body.strip()),
            )
        )

    return result


def _description_from_meta(meta: dict[str, Any], feature: str) -> str | None:
    """Return the template's explicit ``description`` frontmatter, if any.

    Returns ``None`` when missing so the resolution chain in
    :func:`export_skills` falls through to body extraction and finally
    to a generic stub.
    """
    explicit = str(meta.get("description") or "").strip()
    return explicit or None
