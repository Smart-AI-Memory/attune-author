"""Security tests for the MCP path-validation surface.

Focused on adversarial inputs — path traversal, null-byte
injection, symlink escapes, prefix-boundary confusion, and
non-string types — across both the validator and every MCP
handler that consumes a user-controlled path.

Complements test_mcp_server.py, which covers the happy-path
and basic negative cases.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

from attune_author.mcp.handlers import AttuneAuthorHandlers
from attune_author.mcp.path_validation import validate_file_path

# -- Validator: dangerous system prefixes ----------------------------


@pytest.mark.parametrize(
    "system_path",
    [
        "/etc",
        "/sys",
        "/proc",
        "/dev",
        "/boot",
        "/root",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
        "/private/etc",
        "/private/sys",
        "/private/proc",
        "/private/dev",
        "/private/boot",
        "/private/root",
    ],
)
def test_rejects_every_listed_system_prefix(system_path: str) -> None:
    """Every prefix in the blocklist must be rejected at the input stage.

    The pre-resolve check is what blocks macOS symlink bypasses
    (e.g., /etc -> /private/etc), so this must fire on the raw
    input, not only on the resolved path.
    """
    with pytest.raises(ValueError, match="system directory"):
        validate_file_path(system_path)


@pytest.mark.parametrize(
    "system_child",
    [
        "/etc/passwd",
        "/etc/shadow",
        "/root/.ssh/authorized_keys",
        "/bin/sh",
        "/usr/bin/python",
        "/private/etc/hosts",
    ],
)
def test_rejects_children_of_system_prefixes(system_child: str) -> None:
    """Children of blocked prefixes must also be rejected."""
    with pytest.raises(ValueError, match="system directory"):
        validate_file_path(system_child)


@pytest.mark.parametrize(
    "lookalike",
    [
        "/etcd",  # not /etc
        "/etcetera",  # not /etc
        "/rooter",  # not /root
        "/binary",  # not /bin
        "/sbine",  # not /sbin
        "/devops",  # not /dev
    ],
)
def test_prefix_boundary_does_not_overmatch(tmp_path: Path, lookalike: str) -> None:
    """`/etcd` must not be rejected as though it were `/etc`.

    The blocklist match is anchored on either an exact equality
    or the prefix followed by ``/``; anything else is a false
    positive. We point `allowed_dir` at `tmp_path` so the
    workspace-containment check rejects the path (as expected)
    with a *different* error than the system-directory one.
    """
    with pytest.raises(ValueError) as exc_info:
        validate_file_path(lookalike, allowed_dir=str(tmp_path))
    assert "system directory" not in str(exc_info.value)


# -- Validator: null-byte injection ----------------------------------


@pytest.mark.parametrize(
    "poisoned",
    [
        "\x00",
        "\x00leading",
        "trailing\x00",
        "mid\x00dle",
        "nested/\x00/path",
    ],
)
def test_rejects_null_bytes_in_any_position(poisoned: str) -> None:
    with pytest.raises(ValueError, match="null bytes"):
        validate_file_path(poisoned)


# -- Validator: non-string inputs ------------------------------------


@pytest.mark.parametrize(
    "bad_input",
    [None, 42, 3.14, b"/tmp", ["/tmp"], {"path": "/tmp"}, object()],
)
def test_rejects_non_string_inputs(bad_input: object) -> None:
    """Non-string types must be rejected before any path logic runs.

    Guards against a caller accidentally passing a bytes path or
    a Path object (both of which would bypass string-based
    sanitization downstream).
    """
    with pytest.raises(ValueError, match="non-empty string"):
        validate_file_path(bad_input)  # type: ignore[arg-type]


# -- Validator: traversal and symlink escapes ------------------------


def test_relative_traversal_escaping_workspace_is_rejected(
    tmp_path: Path,
) -> None:
    """`../../etc/passwd` style inputs must not escape the workspace.

    The validator calls `.resolve()` on the raw path, which
    collapses `..` segments — so the containment check is what
    has to catch this, not the system-prefix blocklist.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises(ValueError):
        validate_file_path(
            str(workspace / ".." / ".." / "outside.txt"),
            allowed_dir=str(workspace),
        )


def test_direct_symlink_to_system_dir_rejected(tmp_path: Path) -> None:
    """A single symlink whose target is a system dir must fail."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    link = workspace / "shortcut"
    link.symlink_to("/etc")

    with pytest.raises(ValueError):
        validate_file_path(str(link), allowed_dir=str(workspace))


def test_symlink_inside_workspace_escaping_to_tmp_rejected(
    tmp_path: Path,
) -> None:
    """A symlink that escapes the workspace (but not to a system
    dir) must still be rejected by the containment check."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    (other / "secret.txt").write_text("x")

    link = workspace / "escape"
    link.symlink_to(other / "secret.txt")

    with pytest.raises(ValueError, match="outside allowed directory"):
        validate_file_path(str(link), allowed_dir=str(workspace))


def test_whitespace_only_path_rejected() -> None:
    """Whitespace-only paths are truthy strings but nonsensical.

    Documents the current behavior: the validator accepts them as
    non-empty and lets Path resolve them (which treats them as
    file names in CWD). If policy later tightens, this test
    should be updated rather than silently changing semantics.
    """
    # This test pins current behavior — a pure whitespace string
    # is resolved relative to CWD, not rejected outright.
    result = validate_file_path("   ")
    assert isinstance(result, Path)


# -- Handler-level: every path-taking MCP tool rejects traversal -----


@pytest.fixture
def handlers(tmp_path: Path) -> AttuneAuthorHandlers:
    return AttuneAuthorHandlers(workspace_root=str(tmp_path))


@pytest.fixture
def traversal_path() -> str:
    """An absolute system-directory path that every handler must refuse."""
    return "/etc"


def test_author_init_rejects_traversal_in_project_root(
    handlers: AttuneAuthorHandlers, traversal_path: str
) -> None:
    result = asyncio.run(handlers.author_init({"project_root": traversal_path}))
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_status_rejects_traversal_in_help_dir(
    handlers: AttuneAuthorHandlers, traversal_path: str, tmp_path: Path
) -> None:
    result = asyncio.run(
        handlers.author_status({"help_dir": traversal_path, "project_root": str(tmp_path)})
    )
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_status_rejects_traversal_in_project_root(
    handlers: AttuneAuthorHandlers, traversal_path: str, tmp_path: Path
) -> None:
    result = asyncio.run(
        handlers.author_status(
            {"help_dir": str(tmp_path / ".help"), "project_root": traversal_path}
        )
    )
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_generate_rejects_traversal_before_manifest_load(
    handlers: AttuneAuthorHandlers, traversal_path: str, tmp_path: Path
) -> None:
    """Path validation must fire before load_manifest — so we
    should see a system-directory error, not a missing-manifest
    error, when a bad path is supplied."""
    result = asyncio.run(
        handlers.author_generate(
            {
                "feature": "anything",
                "help_dir": traversal_path,
                "project_root": str(tmp_path),
            }
        )
    )
    assert result["success"] is False
    assert "system directory" in result["error"]
    assert "manifest" not in result["error"].lower()


def test_author_maintain_rejects_traversal_in_help_dir(
    handlers: AttuneAuthorHandlers, traversal_path: str, tmp_path: Path
) -> None:
    result = asyncio.run(
        handlers.author_maintain({"help_dir": traversal_path, "project_root": str(tmp_path)})
    )
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_lookup_rejects_traversal_in_help_dir(
    handlers: AttuneAuthorHandlers, traversal_path: str
) -> None:
    result = asyncio.run(handlers.author_lookup({"query": "foo", "help_dir": traversal_path}))
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_docs_rejects_traversal_in_existing_target(handlers: AttuneAuthorHandlers) -> None:
    """When `target` points at an existing file, it is validated.

    /etc/hosts exists on every test host — the handler must
    refuse to treat it as a doc source.
    """
    if not Path("/etc/hosts").exists():
        pytest.skip("requires /etc/hosts to exist")
    result = asyncio.run(handlers.author_docs({"target": "/etc/hosts"}))
    assert result["success"] is False
    assert "system directory" in result["error"]


def test_author_docs_rejects_output_parent_in_system_dir(
    handlers: AttuneAuthorHandlers,
) -> None:
    """Output_path parent must be validated *before* mkdir.

    Attempting `/etc/attune-out/doc.md` should fail and never
    touch the filesystem. On Unix the dangerous-prefix rule
    fires ("system directory"); on Windows `/etc` is neither
    a system dir nor under the workspace, so the containment
    rule fires ("outside allowed directory"). Both outcomes
    satisfy the security contract — the write must not land.
    """
    result = asyncio.run(
        handlers.author_docs(
            {
                "target": "def f(): pass",
                "output_path": "/etc/attune-out/doc.md",
            }
        )
    )
    assert result["success"] is False
    err = result["error"]
    assert (
        "system directory" in err or "outside allowed directory" in err
    ), f"expected rejection by system-dir or containment rule, got: {err!r}"
    assert not Path("/etc/attune-out").exists()


# -- Handler-level: workspace containment is enforced ----------------


def test_handler_rejects_path_outside_workspace_root(
    handlers: AttuneAuthorHandlers, tmp_path: Path
) -> None:
    """Even a non-system path must be refused if it escapes the
    pinned workspace_root — guards against /tmp-style escapes
    that bypass the dangerous-prefix check."""
    sibling = tmp_path.parent / "not-the-workspace"
    sibling.mkdir(exist_ok=True)
    try:
        result = asyncio.run(handlers.author_init({"project_root": str(sibling)}))
        assert result["success"] is False
        assert "outside allowed directory" in result["error"]
    finally:
        # tmp_path.parent is pytest's parent tmp, safe to leave sibling
        pass


# -- Defense-in-depth: feature name check inside author_lookup -------


def test_author_lookup_defense_in_depth_blocks_unsafe_feature_name(
    tmp_path: Path,
) -> None:
    """Even if a bad name slips past the manifest loader, the
    MCP handler's extra `is_safe_feature_name` gate must catch
    it before the name is joined into the help-dir path.

    We simulate that by patching `resolve_topic` to return a
    traversal name — a manifest corrupted at rest, a future
    bypass, etc.
    """
    from unittest.mock import patch

    help_dir = tmp_path / ".help"
    help_dir.mkdir()
    (help_dir / "features.yaml").write_text(
        "version: 1\nfeatures:\n  foo:\n    description: Foo\n",
        encoding="utf-8",
    )

    h = AttuneAuthorHandlers(workspace_root=str(tmp_path))
    with patch(
        "attune_author.manifest.resolve_topic",
        return_value="../../../etc/passwd",
    ):
        result = asyncio.run(h.author_lookup({"query": "foo", "help_dir": str(help_dir)}))
    assert result["success"] is False
    assert "Invalid feature name" in result["error"]


# -- Error-shape contract --------------------------------------------


def test_path_validation_error_carries_success_false(
    handlers: AttuneAuthorHandlers,
) -> None:
    """Every path-validation failure must return a dict shaped
    ``{"success": False, "error": <str>}`` — the MCP protocol
    contract the caller relies on. If this regresses, clients
    that key on `result["success"]` will crash."""
    result = asyncio.run(handlers.author_init({"project_root": "/etc"}))
    assert set(result.keys()) >= {"success", "error"}
    assert result["success"] is False
    assert isinstance(result["error"], str) and result["error"]


# -- Platform-specific: Windows path separators on POSIX -------------


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Windows separators are meaningful on Windows",
)
def test_backslash_in_path_on_posix_is_treated_as_literal(
    tmp_path: Path,
) -> None:
    """On POSIX, backslash is a legal filename character, not a
    separator. We pin this behavior so a future refactor that
    starts splitting on `\\` doesn't silently change meaning."""
    weird = tmp_path / "a\\b"
    weird.mkdir()
    result = validate_file_path(str(weird), allowed_dir=str(tmp_path))
    assert result == weird.resolve()
