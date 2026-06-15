"""Tests for the per-page maintenance contract (regen safety).

The core guarantee under test: regeneration NEVER drops hand-written
content. ``manual`` pages are skipped; ``hybrid`` pages keep their
fenced regions; any ambiguous fence structure fails safe to the
on-disk file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from attune_author.maintenance_contract import (
    AUTO,
    HYBRID,
    MANUAL,
    MANUAL_FENCE_END,
    MANUAL_FENCE_START,
    HybridMergeError,
    extract_manual_regions,
    merge_hybrid,
    read_maintenance_mode,
    resolve_write_content,
)


def _fenced(body: str) -> str:
    return f"{MANUAL_FENCE_START}{body}{MANUAL_FENCE_END}"


def _doc(
    maintenance: str | None = None, status: str | None = None, body: str = "x"
) -> str:
    lines = ["---", "type: help-concept"]
    if maintenance is not None:
        lines.append(f"maintenance: {maintenance}")
    if status is not None:
        lines.append(f"status: {status}")
    lines += ["---", body, ""]
    return "\n".join(lines)


class TestReadMaintenanceMode:
    def test_absent_defaults_auto(self) -> None:
        assert read_maintenance_mode(_doc()) == AUTO

    def test_no_frontmatter_defaults_auto(self) -> None:
        assert read_maintenance_mode("# just a heading\n") == AUTO

    @pytest.mark.parametrize("mode", [AUTO, MANUAL, HYBRID])
    def test_explicit_modes(self, mode: str) -> None:
        assert read_maintenance_mode(_doc(maintenance=mode)) == mode

    def test_status_manual_is_alias(self) -> None:
        assert read_maintenance_mode(_doc(status="manual")) == MANUAL

    def test_unknown_value_fails_open_to_auto(self) -> None:
        assert read_maintenance_mode(_doc(maintenance="frozen")) == AUTO

    def test_case_insensitive(self) -> None:
        assert read_maintenance_mode(_doc(maintenance="Hybrid")) == HYBRID

    def test_maintenance_field_wins_over_status(self) -> None:
        # An explicit maintenance:auto un-freezes a legacy status:manual.
        assert read_maintenance_mode(_doc(maintenance="auto", status="manual")) == AUTO


class TestFenceExtraction:
    def test_extracts_regions_in_order(self) -> None:
        text = "intro" + _fenced("ALPHA") + "mid" + _fenced("BETA") + "end"
        assert extract_manual_regions(text) == ["ALPHA", "BETA"]

    def test_no_fences(self) -> None:
        assert extract_manual_regions("nothing here") == []


class TestMergeHybrid:
    def test_preserves_existing_regions_takes_new_auto_text(self) -> None:
        existing = "OLD-AUTO" + _fenced("HANDWRITTEN") + "OLD-TAIL"
        regenerated = "NEW-AUTO" + _fenced("placeholder") + "NEW-TAIL"
        merged = merge_hybrid(regenerated=regenerated, existing=existing)
        assert "NEW-AUTO" in merged and "NEW-TAIL" in merged
        assert "HANDWRITTEN" in merged
        assert "placeholder" not in merged
        assert "OLD-AUTO" not in merged

    def test_multiple_regions_matched_by_order(self) -> None:
        existing = _fenced("A") + "x" + _fenced("B")
        regenerated = _fenced("1") + "y" + _fenced("2")
        merged = merge_hybrid(regenerated=regenerated, existing=existing)
        assert extract_manual_regions(merged) == ["A", "B"]
        assert "y" in merged  # new auto text between regions

    def test_count_mismatch_raises(self) -> None:
        with pytest.raises(HybridMergeError):
            merge_hybrid(regenerated="no fences", existing=_fenced("KEEP"))

    def test_unbalanced_existing_raises(self) -> None:
        with pytest.raises(HybridMergeError):
            merge_hybrid(
                regenerated=_fenced("x"),
                existing=MANUAL_FENCE_START + "dangling",
            )

    def test_nested_fences_raise(self) -> None:
        nested = MANUAL_FENCE_START + _fenced("inner") + MANUAL_FENCE_END
        with pytest.raises(HybridMergeError):
            merge_hybrid(regenerated=_fenced("x"), existing=nested)


class TestResolveWriteContent:
    def test_no_existing_file_returns_regenerated(self, tmp_path: Path) -> None:
        out = tmp_path / "concept.md"
        assert resolve_write_content(out, "NEW") == "NEW"

    def test_auto_returns_regenerated(self, tmp_path: Path) -> None:
        out = tmp_path / "concept.md"
        out.write_text(_doc(maintenance="auto", body="OLD"), encoding="utf-8")
        regenerated = _doc(maintenance="auto", body="NEW")
        assert "NEW" in resolve_write_content(out, regenerated)

    def test_hybrid_merges_and_carries_field(self, tmp_path: Path) -> None:
        out = tmp_path / "concept.md"
        out.write_text(
            _doc(maintenance="hybrid", body="OLD-AUTO" + _fenced("KEEPME")),
            encoding="utf-8",
        )
        # Regenerated comes from the template: fences present, field absent.
        regenerated = _doc(body="NEW-AUTO" + _fenced("placeholder"))
        result = resolve_write_content(out, regenerated)
        assert "KEEPME" in result  # hand-written region preserved
        assert "NEW-AUTO" in result  # auto text refreshed
        assert "placeholder" not in result
        assert read_maintenance_mode(result) == HYBRID  # field carried over

    def test_hybrid_failsafe_keeps_existing_when_fences_mismatch(
        self, tmp_path: Path
    ) -> None:
        out = tmp_path / "concept.md"
        existing = _doc(maintenance="hybrid", body="OLD" + _fenced("PRECIOUS"))
        out.write_text(existing, encoding="utf-8")
        # Template emitted NO fences -> can't place the region -> fail safe.
        regenerated = _doc(body="NEW with no fences")
        result = resolve_write_content(out, regenerated)
        assert result == existing  # untouched; PRECIOUS never dropped
        assert "PRECIOUS" in result
