"""Per-kind incremental polish skip (polish-cost-reduction lever 2).

A template kind whose deterministic pre-polish scaffold is unchanged
vs. the scaffold that produced the on-disk file is skipped entirely:
no polish call, polished body kept verbatim, deterministic metadata
(source_hash / generated_at) refreshed in place so feature-level
staleness clears. See attune-ai docs/specs/polish-cost-reduction/ D3.
"""

from __future__ import annotations

from pathlib import Path

from attune_author.generator import (
    _inject_scaffold_hash,
    _read_scaffold_hash,
    compute_scaffold_hash,
    prepare_polish_phase,
)
from attune_author.manifest import Feature


def _make_feature(tmp_path: Path, body: str = "def hello() -> str:\n    return 'hi'\n") -> Feature:
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "mod.py").write_text(body, encoding="utf-8")
    return Feature(
        name="demo",
        description="Demo feature",
        files=["src/**/*.py"],
        tags=["demo"],
    )


def _prepare(tmp_path: Path, feature: Feature, **kwargs):
    return prepare_polish_phase(
        feature,
        help_dir=tmp_path / ".help",
        project_root=tmp_path,
        depths=["concept"],
        use_rag=False,
        **kwargs,
    )


class TestComputeScaffoldHash:
    def test_stable_under_metadata_changes(self) -> None:
        a = "---\nfeature: x\nsource_hash: aaa\ngenerated_at: 2026-01-01T00:00:00\n---\n\nBody.\n"
        b = "---\nfeature: x\nsource_hash: bbb\ngenerated_at: 2026-06-10T12:34:56\n---\n\nBody.\n"
        assert compute_scaffold_hash(a) == compute_scaffold_hash(b)

    def test_changes_when_body_changes(self) -> None:
        a = "---\nfeature: x\n---\n\nBody one.\n"
        b = "---\nfeature: x\n---\n\nBody two.\n"
        assert compute_scaffold_hash(a) != compute_scaffold_hash(b)

    def test_invariant_to_its_own_injection(self) -> None:
        content = "---\nfeature: x\n---\n\nBody.\n"
        h = compute_scaffold_hash(content)
        injected = _inject_scaffold_hash(content, h, is_project_doc=False)
        assert compute_scaffold_hash(injected) == h


class TestInjectAndRead:
    def test_frontmatter_round_trip(self, tmp_path: Path) -> None:
        content = "---\nfeature: x\ndepth: concept\n---\n\nBody.\n"
        h = compute_scaffold_hash(content)
        injected = _inject_scaffold_hash(content, h, is_project_doc=False)
        f = tmp_path / "concept.md"
        f.write_text(injected, encoding="utf-8")
        assert _read_scaffold_hash(f) == h

    def test_doc_footer_round_trip(self, tmp_path: Path) -> None:
        content = (
            "# Title\n\nBody.\n"
            "<!-- attune-generated: source_hash=abc feature=x kind=how-to"
            " generated_at=2026-06-10 -->\n"
        )
        h = compute_scaffold_hash(content)
        injected = _inject_scaffold_hash(content, h, is_project_doc=True)
        f = tmp_path / "how-to.md"
        f.write_text(injected, encoding="utf-8")
        assert _read_scaffold_hash(f) == h

    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        assert _read_scaffold_hash(tmp_path / "nope.md") is None

    def test_file_without_hash_returns_none(self, tmp_path: Path) -> None:
        f = tmp_path / "old.md"
        f.write_text("---\nfeature: x\n---\n\nPre-lever-2 file.\n", encoding="utf-8")
        assert _read_scaffold_hash(f) is None


class TestPerKindSkip:
    def test_unchanged_scaffold_is_skipped(self, tmp_path: Path) -> None:
        feature = _make_feature(tmp_path)
        prep1 = _prepare(tmp_path, feature)
        assert [p.depth for p in prep1.pending] == ["concept"]
        # Simulate the write phase (no polish): the rendered content
        # already carries scaffold_hash.
        entry = prep1.pending[0]
        entry.out_path.write_text(entry.rendered_content, encoding="utf-8")

        prep2 = _prepare(tmp_path, feature)
        assert prep2.pending == (), "unchanged scaffold must not re-polish"

    def test_skip_keeps_polished_body_and_refreshes_metadata(self, tmp_path: Path) -> None:
        feature = _make_feature(tmp_path)
        prep1 = _prepare(tmp_path, feature)
        entry = prep1.pending[0]
        # Pretend polish improved the body but kept frontmatter; also
        # backdate source_hash to simulate a semantic-only source bump.
        polished = entry.rendered_content.replace("source_hash: ", "source_hash: stale")
        polished += "\nPolished sentence the LLM added.\n"
        entry.out_path.write_text(polished, encoding="utf-8")

        prep2 = _prepare(tmp_path, feature)
        assert prep2.pending == ()
        refreshed = entry.out_path.read_text(encoding="utf-8")
        assert "Polished sentence the LLM added." in refreshed
        assert "source_hash: stale" not in refreshed, "metadata must refresh"
        assert f"source_hash: {prep2.source_hash}" in refreshed

    def test_body_affecting_source_change_repolishes(self, tmp_path: Path) -> None:
        feature = _make_feature(tmp_path)
        prep1 = _prepare(tmp_path, feature)
        entry = prep1.pending[0]
        entry.out_path.write_text(entry.rendered_content, encoding="utf-8")

        # New public function changes the extracted source info → body.
        (tmp_path / "src" / "mod.py").write_text(
            "def hello() -> str:\n    return 'hi'\n\n\ndef goodbye() -> str:\n    return 'bye'\n",
            encoding="utf-8",
        )
        prep2 = _prepare(tmp_path, feature)
        assert [p.depth for p in prep2.pending] == ["concept"]

    def test_missing_file_is_generated(self, tmp_path: Path) -> None:
        feature = _make_feature(tmp_path)
        prep = _prepare(tmp_path, feature)
        assert [p.depth for p in prep.pending] == ["concept"]

    def test_overwrite_bypasses_skip(self, tmp_path: Path) -> None:
        feature = _make_feature(tmp_path)
        prep1 = _prepare(tmp_path, feature)
        entry = prep1.pending[0]
        entry.out_path.write_text(entry.rendered_content, encoding="utf-8")

        prep2 = _prepare(tmp_path, feature, overwrite=True)
        assert [p.depth for p in prep2.pending] == ["concept"]

    def test_pre_lever2_file_without_hash_repolishes_once_then_skips(
        self, tmp_path: Path
    ) -> None:
        feature = _make_feature(tmp_path)
        prep1 = _prepare(tmp_path, feature)
        entry = prep1.pending[0]
        # Strip the scaffold_hash line to simulate a pre-lever-2 file.
        legacy = "\n".join(
            ln for ln in entry.rendered_content.splitlines() if "scaffold_hash" not in ln
        )
        entry.out_path.write_text(legacy + "\n", encoding="utf-8")

        prep2 = _prepare(tmp_path, feature)
        assert [p.depth for p in prep2.pending] == ["concept"], "legacy file regenerates once"
        prep2.pending[0].out_path.write_text(prep2.pending[0].rendered_content, encoding="utf-8")
        prep3 = _prepare(tmp_path, feature)
        assert prep3.pending == (), "then carries the hash and skips"
