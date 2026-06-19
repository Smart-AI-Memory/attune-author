"""Shared test fixtures for attune-author."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

# Real home-dir state this layer's tests must never touch (they isolate via the
# ATTUNE_AUTHOR_POLISH_CACHE env override). The guard below is a regression
# alarm — see specs/test-isolation-guard/ and the workspace testing-conventions.md.
_GUARDED_PATHS = [Path.home() / ".attune" / "polish_cache"]


def _home_snapshot(p: Path):
    """Comparable snapshot: dir → child names; file → mtime; absent → None."""
    if p.is_dir():
        return frozenset(c.name for c in p.iterdir())
    if p.exists():
        return ("file", p.stat().st_mtime)
    return None


@pytest.fixture(scope="session", autouse=True)
def _guard_real_home_state():
    """Fail the run if any test wrote to real home-dir state (missing isolation)."""
    before = {p: _home_snapshot(p) for p in _GUARDED_PATHS}
    yield
    leaked = []
    for p in _GUARDED_PATHS:
        b, a = before[p], _home_snapshot(p)
        if isinstance(b, frozenset) or isinstance(a, frozenset):
            new = (a or frozenset()) - (b or frozenset())
            if new:
                leaked.append(f"{p}: new entries {sorted(new)[:5]}")
        elif b != a:
            leaked.append(f"{p}: created or modified")
    assert not leaked, (
        "Tests wrote to real home-dir state (missing isolation):\n  "
        + "\n  ".join(leaked)
        + "\nIsolate via the tmp-dir fixture — see testing-conventions.md."
    )


@pytest.fixture(autouse=True)
def _lenient_polish_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    """Disable strict polish mode for every test by default.

    Polish is strict in production (a missing API key raises),
    but the test suite deliberately runs without credentials
    and mocks the LLM call where needed. This fixture sets
    ``ATTUNE_AUTHOR_STRICT_POLISH=false`` for every test so
    the generator's polish pass degrades to a no-op when no
    test has mocked ``_call_llm``. Tests that specifically
    exercise strict-mode behavior override it with their own
    ``patch.dict`` block.

    The polish cache directory is also pointed at a per-test
    tmp directory. Without this, every test would share the
    dev machine's real ``~/.attune/polish_cache``, so a
    previous live ``regenerate`` run can populate the cache
    with polished output and cause golden-snapshot tests to
    silently observe LLM-rewritten content instead of the
    deterministic Jinja-only fallback. The behavior is
    environment-dependent and surfaces as flakes between
    machines (or between sessions on the same machine).
    """
    monkeypatch.setenv("ATTUNE_AUTHOR_STRICT_POLISH", "false")
    monkeypatch.setenv(
        "ATTUNE_AUTHOR_POLISH_CACHE",
        str(tmp_path_factory.mktemp("polish_cache")),
    )
    # Also make sure the tests never accidentally call the
    # real Anthropic API with a key picked up from the dev
    # machine's environment — a huge cost/latency hazard.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # The delenv above is only half the guarantee: cli.main() calls
    # dotenv.load_dotenv() at startup, and a dev checkout's repo-root
    # .env symlink (-> the sibling project's real key) would re-inject
    # ANTHROPIC_API_KEY right back, reopening the exact hazard. No-op
    # load_dotenv so credential-state stays whatever a test sets, never
    # whatever is on disk. A test that wants to exercise real dotenv
    # loading restores it with its own monkeypatch.setattr.
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    # Pin LLM auth routing to the API path and hide any ambient
    # Claude Code session. Without this, running the suite inside
    # Claude Code (CLAUDECODE=1) would auto-route un-mocked polish
    # calls to REAL subscription calls via the Agent SDK — the
    # subscription twin of the API-key hazard above. Auth-routing
    # tests override these per-test.
    monkeypatch.setenv("ATTUNE_AUTHOR_AUTH_MODE", "api")
    monkeypatch.delenv("CLAUDECODE", raising=False)
    yield


@pytest.fixture(autouse=True)
def _reset_rag_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset the module-level RagPipeline singleton before each test.

    ground_polish_context() caches the pipeline after first construction.
    Tests that patch attune_rag.RagPipeline need the singleton to be None
    so the patch intercepts construction rather than being bypassed.
    """
    import attune_author.rag_hook as _rh

    monkeypatch.setattr(_rh, "_PIPELINE", None)


@pytest.fixture
def help_dir(tmp_path: Path) -> Path:
    """Create a .help/ directory with a features.yaml."""
    help = tmp_path / ".help"
    help.mkdir()

    features_yaml = help / "features.yaml"
    features_yaml.write_text(
        "version: 1\n"
        "\n"
        "features:\n"
        "  auth:\n"
        "    description: Authentication and authorization\n"
        "    files:\n"
        "      - src/auth/**\n"
        "    tags: [security, users]\n"
        "  cli:\n"
        "    description: Command-line interface\n"
        "    files:\n"
        "      - src/cli.py\n"
        "    tags: [cli, commands]\n",
        encoding="utf-8",
    )
    return help


@pytest.fixture
def project_root(tmp_path: Path, help_dir: Path) -> Path:
    """Create a minimal project structure."""
    # Source files
    src = tmp_path / "src"
    src.mkdir()

    auth_dir = src / "auth"
    auth_dir.mkdir()

    (auth_dir / "__init__.py").write_text(
        '"""Authentication module."""\n',
        encoding="utf-8",
    )
    (auth_dir / "login.py").write_text(
        '"""Login handler."""\n\n\n'
        "def authenticate(username: str, password: str) -> bool:\n"
        '    """Authenticate a user.\n\n'
        "    Args:\n"
        "        username: The username.\n"
        "        password: The password.\n\n"
        "    Returns:\n"
        "        True if authenticated.\n"
        '    """\n'
        "    return True\n",
        encoding="utf-8",
    )

    (src / "cli.py").write_text(
        '"""CLI entry point."""\n\n\n'
        "def main() -> None:\n"
        '    """Run the CLI."""\n'
        "    pass\n",
        encoding="utf-8",
    )

    return tmp_path
