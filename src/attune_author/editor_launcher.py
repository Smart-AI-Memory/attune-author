"""Sidecar lifecycle helper for ``attune-author edit``.

The editor surface lives in attune-gui, which runs as a local FastAPI
sidecar. This module is the bridge from the CLI side: read the
portfile attune-gui writes at ``~/.attune/sidecar.port``, validate the
process is still alive via ``GET /healthz?token=...``, and spawn a
fresh sidecar if either check fails.

We deliberately do **not** import from attune-gui — the portfile JSON
schema (``{pid, port, token}``) is the contract between the two
packages, and reading it as raw JSON keeps attune-author free of an
attune-gui runtime dependency.

Public API:

- :class:`PortfileData` — parsed portfile record.
- :class:`SidecarStartError` — raised when a sidecar can't be brought up.
- :func:`read_portfile`, :func:`is_pid_alive`, :func:`is_healthy`
- :func:`find_existing_sidecar` — read + health-check; returns ``None``
  if the portfile is missing or stale.
- :func:`spawn_sidecar` — launch the ``attune-gui`` command as a child
  process and wait for it to register a fresh portfile.
- :func:`ensure_sidecar` — top-level helper used by the CLI: returns a
  live :class:`PortfileData` regardless of starting state.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_PORTFILE_PATH = Path.home() / ".attune" / "sidecar.port"
_DEFAULT_TIMEOUT = 10.0
_HEALTH_TIMEOUT = 1.0


class SidecarStartError(RuntimeError):
    """Raised when we can't reach a healthy sidecar.

    Carries a ``reason`` machine-readable code so the CLI can produce
    targeted hints (e.g., ``"missing_command"`` → "install attune-gui",
    ``"timeout"`` → "port may be in use").
    """

    def __init__(self, reason: str, message: str) -> None:
        self.reason = reason
        super().__init__(message)


@dataclass(frozen=True)
class PortfileData:
    """Parsed portfile content. Schema is owned by attune-gui."""

    pid: int
    port: int
    token: str

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


# -- portfile + freshness ------------------------------------------


def read_portfile(path: Path = _PORTFILE_PATH) -> PortfileData | None:
    """Return the parsed portfile or ``None`` if missing/corrupt."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    try:
        return PortfileData(
            pid=int(data["pid"]),
            port=int(data["port"]),
            token=str(data["token"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def is_pid_alive(pid: int) -> bool:
    """Return ``True`` if a process with ``pid`` is currently running.

    Dispatches to a platform-specific check. POSIX uses ``os.kill(pid, 0)``;
    Windows uses ``OpenProcess`` + ``GetExitCodeProcess`` via ctypes because
    ``os.kill(pid, 0)`` for a non-existent PID hangs on the GitHub Actions
    Windows runner (and is brittle in general — Windows preserves PID slots
    briefly after a process exits, so signal-style probes can't distinguish
    "running" from "recently dead").
    """
    if pid <= 0:
        return False
    if sys.platform == "win32":
        return _is_pid_alive_win32(pid)
    return _is_pid_alive_posix(pid)


def _is_pid_alive_posix(pid: int) -> bool:
    """POSIX path: probe with signal 0."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists but we lack permission to signal it.
        return True
    except OSError:
        return False
    return True


def _is_pid_alive_win32(pid: int) -> bool:
    """Windows path: open the process and check its exit code.

    ``OpenProcess`` returns NULL when the PID doesn't exist (or we lack
    access — but PROCESS_QUERY_LIMITED_INFORMATION is broadly granted).
    A live process has exit code ``STILL_ACTIVE`` (259); anything else
    means the process has terminated and Windows is just keeping the
    PID slot reserved.
    """
    import ctypes
    from ctypes import wintypes

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259

    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


def is_healthy(port: int, token: str, *, timeout: float = _HEALTH_TIMEOUT) -> bool:
    """``GET /healthz?token=<token>`` — return ``True`` on 200."""
    url = f"http://127.0.0.1:{port}/healthz?token={urllib.parse.quote(token)}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return False


def find_existing_sidecar(path: Path = _PORTFILE_PATH) -> PortfileData | None:
    """Return a healthy :class:`PortfileData` or ``None`` if stale."""
    data = read_portfile(path)
    if data is None:
        return None
    if not is_pid_alive(data.pid):
        return None
    if not is_healthy(data.port, data.token):
        return None
    return data


# -- spawn ---------------------------------------------------------


def spawn_sidecar(
    *,
    port: int | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    portfile_path: Path = _PORTFILE_PATH,
    command: list[str] | None = None,
) -> PortfileData:
    """Launch ``attune-gui`` as a detached child and wait for readiness.

    The child writes its portfile on startup; we poll for it, then
    confirm via ``/healthz``. Raises :class:`SidecarStartError` if the
    binary can't be found or the sidecar fails to come up in
    ``timeout`` seconds.
    """
    cmd = list(command) if command is not None else _default_command()
    if cmd[0] != sys.executable and shutil.which(cmd[0]) is None:
        raise SidecarStartError(
            "missing_command",
            f"Cannot launch sidecar: {cmd[0]!r} not found on PATH. "
            f"Install it with: pip install attune-gui",
        )
    if port is not None:
        cmd = [*cmd, "--port", str(port)]

    # Snapshot the existing portfile so we can tell when the new
    # sidecar has overwritten it. (A leftover stale portfile must not
    # be mistaken for the sidecar we just spawned.)
    pre = read_portfile(portfile_path)

    try:
        proc = subprocess.Popen(  # noqa: S603 — cmd is constructed from a fixed allowlist
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
    except (FileNotFoundError, OSError) as exc:
        raise SidecarStartError("spawn_failed", f"Failed to spawn sidecar process: {exc}") from exc

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            # Child exited before we could connect — surface its stderr.
            stderr = (proc.stderr.read() if proc.stderr else b"").decode("utf-8", errors="replace")
            raise SidecarStartError(
                "child_exited",
                f"Sidecar exited with code {proc.returncode}. stderr: {stderr.strip()!r}",
            )
        data = read_portfile(portfile_path)
        if (
            data is not None
            and (pre is None or data.pid != pre.pid or data.port != pre.port)
            and is_pid_alive(data.pid)
            and is_healthy(data.port, data.token)
        ):
            return data
        time.sleep(0.1)

    # Timed out waiting. Best-effort terminate the child so we don't
    # leak a half-started sidecar.
    proc.terminate()
    raise SidecarStartError(
        "timeout",
        f"Sidecar did not become healthy within {timeout:.0f}s. "
        f"The port may be in use or attune-gui may be misconfigured.",
    )


def _default_command() -> list[str]:
    """Return the command used to launch the sidecar.

    Prefer the installed ``attune-gui`` console script; fall back to
    ``python -m attune_gui.main`` when running from a checkout.
    """
    if shutil.which("attune-gui") is not None:
        return ["attune-gui"]
    return [sys.executable, "-m", "attune_gui.main"]


# -- top-level -----------------------------------------------------


def ensure_sidecar(
    *,
    port: int | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    portfile_path: Path = _PORTFILE_PATH,
) -> PortfileData:
    """Return a healthy sidecar, spawning one if necessary."""
    existing = find_existing_sidecar(portfile_path)
    if existing is not None and (port is None or existing.port == port):
        return existing
    return spawn_sidecar(port=port, timeout=timeout, portfile_path=portfile_path)


__all__ = [
    "PortfileData",
    "SidecarStartError",
    "ensure_sidecar",
    "find_existing_sidecar",
    "is_healthy",
    "is_pid_alive",
    "read_portfile",
    "spawn_sidecar",
]
