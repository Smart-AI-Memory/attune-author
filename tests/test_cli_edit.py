"""Tests for ``attune-author edit`` (template-editor M5 #25, #26).

The CLI is fully isolated from a real sidecar — every test patches
:func:`attune_author.editor_launcher.ensure_sidecar` and the HTTP
helpers in :mod:`attune_author.cli` so no network or subprocess
activity occurs.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from attune_author import cli, editor_launcher
from attune_author.cli import main


@pytest.fixture
def template_file(tmp_path: Path) -> Path:
    f = tmp_path / "alpha.md"
    f.write_text("---\ntype: concept\nname: Alpha\n---\n\nbody\n", encoding="utf-8")
    return f


@pytest.fixture
def fake_sidecar(monkeypatch: pytest.MonkeyPatch) -> editor_launcher.PortfileData:
    data = editor_launcher.PortfileData(pid=1, port=4242, token="t-test")
    monkeypatch.setattr(cli, "ensure_sidecar", lambda **_kw: data, raising=False)
    # ``cli`` imports ensure_sidecar lazily inside _cmd_edit; patch at the source.
    monkeypatch.setattr(editor_launcher, "ensure_sidecar", lambda **_kw: data)
    return data


# -- happy path ----------------------------------------------------


def test_edit_resolves_and_prints_url(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`attune-author edit <path> --no-open` prints the editor URL."""

    def fake_resolve(_sidecar, abs_path):
        assert abs_path == template_file.resolve()
        return ("test-corpus", "alpha.md")

    monkeypatch.setattr(cli, "_resolve_path", fake_resolve)
    monkeypatch.setattr(cli.webbrowser, "open", lambda *_args, **_kw: True)

    rc = main(["edit", str(template_file), "--no-open"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "http://127.0.0.1:4242/editor" in out
    assert "corpus=test-corpus" in out
    assert "path=alpha.md" in out


def test_edit_launches_browser_by_default(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: ("test-corpus", "alpha.md"))
    opened: list[str] = []
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.append(url) or True)

    rc = main(["edit", str(template_file)])
    assert rc == 0
    assert len(opened) == 1
    assert "/editor?" in opened[0]


def test_edit_no_open_does_not_launch_browser(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: ("c", "alpha.md"))
    opened: list[str] = []
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.append(url) or True)

    rc = main(["edit", str(template_file), "--no-open"])
    assert rc == 0
    assert opened == []


# -- edge cases ----------------------------------------------------


def test_edit_path_does_not_exist(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    """Missing path → exit 1 with hint, never reaches the sidecar."""
    rc = main(["edit", str(tmp_path / "ghost.md")])
    assert rc == 1
    err = capsys.readouterr().err
    assert "does not exist" in err


def test_edit_sidecar_start_failure_returns_2(
    template_file: Path,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(**_kw):
        raise editor_launcher.SidecarStartError("missing_command", "attune-gui not on PATH")

    monkeypatch.setattr(cli, "ensure_sidecar", fail)
    rc = main(["edit", str(template_file)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "missing_command" in err
    assert "pip install attune-gui" in err


def test_edit_sidecar_timeout_hint(
    template_file: Path,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(**_kw):
        raise editor_launcher.SidecarStartError("timeout", "did not become healthy")

    monkeypatch.setattr(cli, "ensure_sidecar", fail)
    rc = main(["edit", str(template_file)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "port may be in use" in err


def test_edit_unregistered_path_non_interactive_exits_1(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the path is outside every corpus and stdin isn't a TTY,
    print a hint and exit 1 (no interactive prompt)."""
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: None)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)

    rc = main(["edit", str(template_file)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "not inside any registered corpus" in err
    assert "Suggested root" in err


def test_edit_unregistered_path_declined_at_prompt_exits_1(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: None)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    rc = main(["edit", str(template_file)])
    assert rc == 1


def test_edit_unregistered_path_accepted_registers_and_opens(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: None)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt: "y")

    register_calls = {"n": 0}

    def fake_urlopen(req, **_kw):
        register_calls["n"] += 1
        # Confirm the right endpoint was hit.
        assert req.full_url.endswith("/api/corpus/register")
        body = json.loads(req.data)
        assert body["path"] == str(template_file.parent.resolve())
        resp = MagicMock()
        resp.read.return_value = json.dumps(
            {"id": "ad-hoc-1", "name": body["name"], "path": body["path"], "kind": "ad-hoc"}
        ).encode()
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        return resp

    monkeypatch.setattr(cli.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(cli.webbrowser, "open", lambda *_a, **_kw: True)

    rc = main(["edit", str(template_file)])
    assert rc == 0
    assert register_calls["n"] == 1
    out = capsys.readouterr().out
    assert "corpus=ad-hoc-1" in out


# -- --corpus override ---------------------------------------------


def test_edit_with_explicit_corpus_skips_resolve(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--corpus <id>` looks up the root via /api/corpus, no /resolve call."""
    monkeypatch.setattr(cli.webbrowser, "open", lambda *_a, **_kw: True)

    def fake_corpus_root(_sidecar, corpus_id):
        assert corpus_id == "explicit"
        return template_file.parent

    monkeypatch.setattr(cli, "_corpus_root", fake_corpus_root)
    # _resolve_path must not be called when --corpus is given.
    monkeypatch.setattr(cli, "_resolve_path", lambda *_a: pytest.fail("_resolve_path was called"))

    rc = main(["edit", str(template_file), "--corpus", "explicit", "--no-open"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "corpus=explicit" in out
    assert "path=alpha.md" in out


def test_edit_with_explicit_corpus_path_outside_root_exits_1(
    template_file: Path,
    fake_sidecar: editor_launcher.PortfileData,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "_corpus_root", lambda *_a: Path("/some/other/place"))

    rc = main(["edit", str(template_file), "--corpus", "explicit", "--no-open"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "not inside corpus" in err
