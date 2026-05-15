"""Tests for the fact-check hook in ``generator.apply_polish_results``."""

from __future__ import annotations

from pathlib import Path

import pytest

from attune_author.fact_check import FactCheckError
from attune_author.generator import _run_fact_check


def test_run_fact_check_off_is_noop(tmp_path: Path, monkeypatch) -> None:
    """``ATTUNE_AUTHOR_FACT_CHECK=off`` short-circuits before reading the file."""
    monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "off")
    file = tmp_path / "polished.md"
    file.write_text("[broken](nope.md)\n", encoding="utf-8")
    _run_fact_check(file)
    # Unchanged.
    assert file.read_text(encoding="utf-8") == "[broken](nope.md)\n"


def test_run_fact_check_soft_appends_block(tmp_path: Path, monkeypatch) -> None:
    """Default soft mode writes the unresolved-references block."""
    monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "soft")
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "polished.md"
    file.write_text("[broken](nope.md)\n", encoding="utf-8")
    _run_fact_check(file)
    text = file.read_text(encoding="utf-8")
    assert "## Unresolved references" in text
    assert "nope.md" in text


def test_run_fact_check_strict_raises(tmp_path: Path, monkeypatch) -> None:
    """Strict mode raises ``FactCheckError`` on error-severity findings."""
    monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "strict")
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "polished.md"
    file.write_text("[broken](nope.md)\n", encoding="utf-8")
    with pytest.raises(FactCheckError) as exc:
        _run_fact_check(file)
    assert "unresolved references" in str(exc.value)


def test_run_fact_check_clean_file_silent(tmp_path: Path, monkeypatch) -> None:
    """No findings → file untouched, no raise even in strict."""
    monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "strict")
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "polished.md"
    body = "# Clean\n\nNothing to flag here.\n"
    file.write_text(body, encoding="utf-8")
    _run_fact_check(file)
    assert file.read_text(encoding="utf-8") == body


def test_run_fact_check_swallows_internal_errors(tmp_path: Path, monkeypatch, caplog) -> None:
    """Any exception inside the fact-check layer logs and returns."""
    monkeypatch.setenv("ATTUNE_AUTHOR_FACT_CHECK", "soft")
    # Point at a nonexistent file so the check raises FileNotFoundError.
    missing = tmp_path / "missing.md"
    # Should not raise.
    _run_fact_check(missing)
