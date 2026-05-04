"""Tests for :mod:`attune_author.editor_launcher` (template-editor M5 #24)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from attune_author import editor_launcher


@pytest.fixture
def portfile(tmp_path: Path) -> Path:
    """Return a per-test portfile path; nothing written yet."""
    return tmp_path / "sidecar.port"


def _write_portfile(path: Path, *, pid: int, port: int, token: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"pid": pid, "port": port, "token": token}), encoding="utf-8")


# -- read_portfile / freshness ---------------------------------------


def test_read_portfile_missing_returns_none(portfile: Path) -> None:
    assert editor_launcher.read_portfile(portfile) is None


def test_read_portfile_corrupt_returns_none(portfile: Path) -> None:
    portfile.parent.mkdir(parents=True, exist_ok=True)
    portfile.write_text("not json", encoding="utf-8")
    assert editor_launcher.read_portfile(portfile) is None


def test_read_portfile_missing_keys_returns_none(portfile: Path) -> None:
    portfile.parent.mkdir(parents=True, exist_ok=True)
    portfile.write_text(json.dumps({"pid": 1}), encoding="utf-8")
    assert editor_launcher.read_portfile(portfile) is None


def test_read_portfile_round_trip(portfile: Path) -> None:
    _write_portfile(portfile, pid=42, port=8765, token="t-abc")
    data = editor_launcher.read_portfile(portfile)
    assert data is not None
    assert data.pid == 42
    assert data.port == 8765
    assert data.token == "t-abc"
    assert data.url == "http://127.0.0.1:8765"


def test_is_pid_alive_for_self() -> None:
    import os

    assert editor_launcher.is_pid_alive(os.getpid()) is True


def test_is_pid_alive_for_dead_pid() -> None:
    # PID 0 is reserved and never a real process.
    assert editor_launcher.is_pid_alive(0) is False
    # A very-likely-dead high PID.
    assert editor_launcher.is_pid_alive(999_999_999) is False


# -- find_existing_sidecar -------------------------------------------


def test_find_existing_returns_none_when_portfile_missing(portfile: Path) -> None:
    assert editor_launcher.find_existing_sidecar(portfile) is None


def test_find_existing_returns_none_when_pid_dead(portfile: Path) -> None:
    _write_portfile(portfile, pid=999_999_999, port=12345, token="t")
    assert editor_launcher.find_existing_sidecar(portfile) is None


def test_find_existing_returns_none_when_health_fails(
    portfile: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os

    _write_portfile(portfile, pid=os.getpid(), port=12345, token="t")
    monkeypatch.setattr(editor_launcher, "is_healthy", lambda *a, **kw: False)
    assert editor_launcher.find_existing_sidecar(portfile) is None


def test_find_existing_returns_data_when_healthy(
    portfile: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os

    _write_portfile(portfile, pid=os.getpid(), port=12345, token="t")
    monkeypatch.setattr(editor_launcher, "is_healthy", lambda *a, **kw: True)
    data = editor_launcher.find_existing_sidecar(portfile)
    assert data is not None
    assert data.port == 12345


# -- spawn_sidecar ---------------------------------------------------


def test_spawn_missing_command_raises(monkeypatch: pytest.MonkeyPatch, portfile: Path) -> None:
    monkeypatch.setattr(editor_launcher.shutil, "which", lambda _name: None)
    monkeypatch.setattr(editor_launcher, "_default_command", lambda: ["nope-no-bin"])
    with pytest.raises(editor_launcher.SidecarStartError) as exc_info:
        editor_launcher.spawn_sidecar(portfile_path=portfile, timeout=0.5)
    assert exc_info.value.reason == "missing_command"


def test_spawn_returns_data_when_child_writes_portfile(
    monkeypatch: pytest.MonkeyPatch, portfile: Path
) -> None:
    """Simulate a healthy sidecar startup."""
    import os

    monkeypatch.setattr(editor_launcher.shutil, "which", lambda _name: "/usr/bin/fake")
    monkeypatch.setattr(editor_launcher, "is_healthy", lambda *a, **kw: True)

    fake_proc = MagicMock()
    fake_proc.poll.return_value = None  # still running

    def fake_popen(_cmd, **_kwargs):
        # Pretend the child wrote a portfile mid-startup.
        _write_portfile(portfile, pid=os.getpid(), port=54321, token="t-fresh")
        return fake_proc

    monkeypatch.setattr(editor_launcher.subprocess, "Popen", fake_popen)

    data = editor_launcher.spawn_sidecar(portfile_path=portfile, timeout=2.0)
    assert data.port == 54321
    assert data.token == "t-fresh"


def test_spawn_surfaces_child_exit(monkeypatch: pytest.MonkeyPatch, portfile: Path) -> None:
    monkeypatch.setattr(editor_launcher.shutil, "which", lambda _name: "/usr/bin/fake")

    fake_proc = MagicMock()
    fake_proc.poll.return_value = 17
    fake_proc.returncode = 17
    fake_proc.stderr.read.return_value = b"boom"
    monkeypatch.setattr(editor_launcher.subprocess, "Popen", lambda *a, **kw: fake_proc)

    with pytest.raises(editor_launcher.SidecarStartError) as exc_info:
        editor_launcher.spawn_sidecar(portfile_path=portfile, timeout=2.0)
    assert exc_info.value.reason == "child_exited"
    assert "boom" in str(exc_info.value)


def test_spawn_times_out(monkeypatch: pytest.MonkeyPatch, portfile: Path) -> None:
    monkeypatch.setattr(editor_launcher.shutil, "which", lambda _name: "/usr/bin/fake")

    fake_proc = MagicMock()
    fake_proc.poll.return_value = None
    monkeypatch.setattr(editor_launcher.subprocess, "Popen", lambda *a, **kw: fake_proc)

    with pytest.raises(editor_launcher.SidecarStartError) as exc_info:
        editor_launcher.spawn_sidecar(portfile_path=portfile, timeout=0.2)
    assert exc_info.value.reason == "timeout"
    fake_proc.terminate.assert_called_once()


# -- ensure_sidecar --------------------------------------------------


def test_ensure_returns_existing_when_healthy(
    monkeypatch: pytest.MonkeyPatch, portfile: Path
) -> None:
    import os

    _write_portfile(portfile, pid=os.getpid(), port=11111, token="t")
    monkeypatch.setattr(editor_launcher, "is_healthy", lambda *a, **kw: True)
    spawn_calls = {"n": 0}

    def fake_spawn(**_kwargs):
        spawn_calls["n"] += 1
        raise AssertionError("spawn should not be called when existing is healthy")

    monkeypatch.setattr(editor_launcher, "spawn_sidecar", fake_spawn)

    data = editor_launcher.ensure_sidecar(portfile_path=portfile)
    assert data.port == 11111
    assert spawn_calls["n"] == 0


def test_ensure_spawns_when_no_existing(monkeypatch: pytest.MonkeyPatch, portfile: Path) -> None:
    spawn_calls = {"n": 0}

    def fake_spawn(**_kwargs):
        spawn_calls["n"] += 1
        return editor_launcher.PortfileData(pid=1, port=2, token="t")

    monkeypatch.setattr(editor_launcher, "spawn_sidecar", fake_spawn)

    data = editor_launcher.ensure_sidecar(portfile_path=portfile)
    assert data.port == 2
    assert spawn_calls["n"] == 1
