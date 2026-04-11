"""Structure tests for the dogfood help system.

These tests assert that ``.help/`` for attune-author itself
is well-formed: every feature listed in ``features.yaml``
has a complete template tree, every template has the right
frontmatter, and the corpus matches the expected counts.

The tests do NOT regenerate templates — they only verify
the committed output. Regeneration is done out-of-band by
``scripts/regenerate_help.py`` (which uses the Anthropic
API and would be wasteful in CI).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from attune_author.generator import _ALL_TEMPLATE_NAMES
from attune_author.manifest import load_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
HELP_DIR = REPO_ROOT / ".help"
TEMPLATES_DIR = HELP_DIR / "templates"


@pytest.fixture(scope="module")
def manifest():
    """Load the dogfood manifest once for the whole module."""
    return load_manifest(HELP_DIR)


@pytest.fixture(scope="module")
def feature_names(manifest) -> list[str]:
    """Names of every feature in the dogfood manifest."""
    return sorted(manifest.features.keys())


@pytest.fixture(scope="module")
def template_kinds() -> list[str]:
    """Every template kind the generator can produce."""
    return list(_ALL_TEMPLATE_NAMES)


class TestManifestStructure:
    """The dogfood features.yaml itself is well-formed."""

    def test_help_directory_exists(self) -> None:
        assert HELP_DIR.is_dir(), "missing .help/ directory"

    def test_features_yaml_exists(self) -> None:
        assert (HELP_DIR / "features.yaml").is_file()

    def test_manifest_loads(self, manifest) -> None:
        assert manifest is not None
        assert manifest.version == 1

    def test_manifest_has_at_least_one_feature(self, manifest) -> None:
        assert len(manifest.features) >= 1

    def test_every_feature_has_description(self, manifest) -> None:
        for name, feature in manifest.features.items():
            assert feature.description, f"feature {name!r} missing description"

    def test_every_feature_has_files(self, manifest) -> None:
        for name, feature in manifest.features.items():
            assert feature.files, f"feature {name!r} has no files"


class TestTemplateTreeStructure:
    """Every feature has a complete template directory."""

    def test_templates_dir_exists(self) -> None:
        assert TEMPLATES_DIR.is_dir(), "missing .help/templates/"

    def test_every_feature_has_a_template_dir(self, feature_names: list[str]) -> None:
        for name in feature_names:
            assert (
                TEMPLATES_DIR / name
            ).is_dir(), f"missing template dir for feature {name!r}"

    def test_no_orphan_template_dirs(self, feature_names: list[str]) -> None:
        """Every directory under templates/ corresponds to a
        feature in features.yaml — guards against stale
        leftovers from removed features.
        """
        on_disk = {
            p.name
            for p in TEMPLATES_DIR.iterdir()
            if p.is_dir() and not p.name.startswith("_")
        }
        expected = set(feature_names)
        assert on_disk == expected, (
            f"orphans: {on_disk - expected}, " f"missing: {expected - on_disk}"
        )

    def test_each_feature_has_all_template_kinds(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        """Every feature has all 11 template kinds rendered."""
        for name in feature_names:
            feature_dir = TEMPLATES_DIR / name
            for kind in template_kinds:
                template_path = feature_dir / f"{kind}.md"
                assert (
                    template_path.is_file()
                ), f"missing {kind}.md for feature {name!r}"

    def test_total_template_count(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        """Total templates on disk equals features × kinds."""
        all_md = list(TEMPLATES_DIR.rglob("*.md"))
        expected = len(feature_names) * len(template_kinds)
        assert (
            len(all_md) == expected
        ), f"expected {expected} templates, found {len(all_md)}"


class TestTemplateFrontmatter:
    """Each generated template has the canonical frontmatter."""

    def _all_templates(self, feature_names: list[str], template_kinds: list[str]):
        for name in feature_names:
            for kind in template_kinds:
                yield name, kind, TEMPLATES_DIR / name / f"{kind}.md"

    def test_every_template_starts_with_frontmatter(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        for _name, _kind, path in self._all_templates(feature_names, template_kinds):
            content = path.read_text(encoding="utf-8")
            assert content.startswith("---\n"), f"{path} missing opening frontmatter"

    def test_every_template_has_type_field(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        for name, kind, path in self._all_templates(feature_names, template_kinds):
            content = path.read_text(encoding="utf-8")
            assert f"type: {kind}" in content, f"{path} missing type: {kind}"

    def test_every_template_has_feature_field(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        for name, _kind, path in self._all_templates(feature_names, template_kinds):
            content = path.read_text(encoding="utf-8")
            assert f"feature: {name}" in content, f"{path} missing feature: {name}"

    def test_every_template_ends_with_newline(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        for _name, _kind, path in self._all_templates(feature_names, template_kinds):
            content = path.read_text(encoding="utf-8")
            assert content.endswith("\n"), f"{path} missing trailing newline"

    def test_no_trailing_whitespace(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        for _name, _kind, path in self._all_templates(feature_names, template_kinds):
            content = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(content.splitlines(), 1):
                assert line == line.rstrip(), f"{path}:{lineno} has trailing whitespace"


class TestNoBoilerplateInPolishedTemplates:
    """Polish-pass invariants on the committed templates.

    These tests check that the polished output does NOT
    contain the verbatim placeholder phrases that appear in
    the raw Jinja2 drafts. If any of these strings show up,
    it means polish was skipped for that template (or the
    polish pass produced an unusable response and the
    fallback path was taken).

    The check is gentle — it allows up to 10% of templates to
    contain a placeholder phrase, since the polish pass can
    legitimately fail occasionally on a long template. A
    higher rate signals a regression in the prompts.
    """

    PLACEHOLDER_PHRASES = (
        "The polish pass replaces this placeholder",
        "The polish pass rewrites this section",
        "The polish pass will adapt these steps",
        "The polish pass replaces this answer",
        "The polish pass rewrites this",
    )

    def test_polish_placeholders_below_threshold(
        self,
        feature_names: list[str],
        template_kinds: list[str],
    ) -> None:
        total = 0
        with_placeholder = 0
        for name in feature_names:
            for kind in template_kinds:
                path = TEMPLATES_DIR / name / f"{kind}.md"
                content = path.read_text(encoding="utf-8")
                total += 1
                if any(p in content for p in self.PLACEHOLDER_PHRASES):
                    with_placeholder += 1

        ratio = with_placeholder / total if total else 0.0
        assert ratio < 0.10, (
            f"{with_placeholder}/{total} templates still "
            f"contain polish placeholders ({ratio:.0%}). "
            f"Re-run scripts/regenerate_help.py with the "
            f"API key set to fix."
        )
