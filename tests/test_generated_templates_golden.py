"""Golden snapshots for generated templates.

Pins the rendered output of ``generate_feature_templates`` for the three
core depths (concept / task / reference). Schema drift in the Jinja2
templates or in the frontmatter contract gets caught at PR time rather
than weeks later via the cross-repo workflow.

Snapshots live in ``tests/__snapshots__/`` (syrupy default). Updating a
snapshot requires the deliberate ``pytest --snapshot-update`` run, so
unintentional output changes show up in PR review as snapshot diffs.

The polish pass is disabled across the suite by the autouse
``_lenient_polish_by_default`` fixture in conftest.py, so the snapshots
capture the deterministic Jinja2-only output (no LLM calls).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from attune_author.generator import generate_feature_templates
from attune_author.manifest import Feature

# syrupy's SnapshotAssertion is provided via the ``snapshot`` fixture
# pulled in automatically when syrupy is installed.

# Volatile frontmatter fields: timestamps + content-hash. Stripped before
# comparing so snapshots stay deterministic across runs.
_TIMESTAMP_RE = re.compile(
    r"(\w+_at: )\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?"
)
_HASH_RE = re.compile(r"(source_hash: )[0-9a-f]+")


def _stable(text: str) -> str:
    """Replace timestamps + hashes with placeholders for snapshot stability."""
    text = _TIMESTAMP_RE.sub(r"\1<TIMESTAMP>", text)
    text = _HASH_RE.sub(r"\1<HASH>", text)
    return text


@pytest.fixture
def auth_feature() -> Feature:
    return Feature(
        name="auth",
        description="Authentication and authorization",
        files=["src/auth/**"],
        tags=["security"],
    )


def _read_template(result, kind: str) -> str:
    """Load a generated template by kind from a GenerationResult."""
    matches = [t for t in result.templates if t.depth == kind]
    assert matches, (
        f"no {kind} template generated; got depths: " f"{[t.depth for t in result.templates]}"
    )
    return matches[0].path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Per-depth golden snapshots
# ---------------------------------------------------------------------------


def test_concept_template_matches_snapshot(
    help_dir: Path, project_root: Path, auth_feature: Feature, snapshot
) -> None:
    """Concept template — high-level conceptual overview."""
    result = generate_feature_templates(
        feature=auth_feature,
        help_dir=help_dir,
        project_root=project_root,
        depths=["concept"],
        use_rag=False,
    )
    rendered = _stable(_read_template(result, "concept"))
    assert rendered == snapshot


def test_task_template_matches_snapshot(
    help_dir: Path, project_root: Path, auth_feature: Feature, snapshot
) -> None:
    """Task template — step-by-step procedure."""
    result = generate_feature_templates(
        feature=auth_feature,
        help_dir=help_dir,
        project_root=project_root,
        depths=["task"],
        use_rag=False,
    )
    rendered = _stable(_read_template(result, "task"))
    assert rendered == snapshot


def test_reference_template_matches_snapshot(
    help_dir: Path, project_root: Path, auth_feature: Feature, snapshot
) -> None:
    """Reference template — exhaustive API/option detail."""
    result = generate_feature_templates(
        feature=auth_feature,
        help_dir=help_dir,
        project_root=project_root,
        depths=["reference"],
        use_rag=False,
    )
    rendered = _stable(_read_template(result, "reference"))
    assert rendered == snapshot


# ---------------------------------------------------------------------------
# Frontmatter schema invariants — independent of snapshot exact-match
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["concept", "task", "reference"])
def test_generated_templates_have_required_frontmatter_fields(
    help_dir: Path, project_root: Path, auth_feature: Feature, kind: str
) -> None:
    """All core templates must carry name + feature + source_hash, regardless
    of the snapshot exact-match diff. Catches schema regressions even if a
    snapshot is updated by mistake."""
    result = generate_feature_templates(
        feature=auth_feature,
        help_dir=help_dir,
        project_root=project_root,
        depths=[kind],
        use_rag=False,
    )
    rendered = _read_template(result, kind)
    assert rendered.startswith("---\n"), "missing frontmatter open fence"
    head, _, _ = rendered[4:].partition("\n---\n")
    for required in ("name:", "feature: auth", "source_hash:"):
        assert required in head, f"{kind} template frontmatter missing {required!r}; got:\n{head}"
