"""Unit tests for the new AST extractors in generator.py.

Covers:
- _extract_raises: exception classes raised by a function
- _extract_literal_values: Literal[...] allowed string values
- _extract_param_literals: per-param literal enumerations
- _is_dataclass: @dataclass decorator detection
- _extract_dataclass_fields: field name/type/default for dataclasses

These feed the polish LLM so the reference template can render
defaults, raises, enum members, and dataclass field tables — the
four gaps the v0.3.6 hallucination benchmark surfaced.
"""

from __future__ import annotations

import ast

from attune_author.generator import (
    _extract_dataclass_fields,
    _extract_literal_values,
    _extract_param_literals,
    _extract_raises,
    _is_dataclass,
)


def _fn(src: str) -> ast.FunctionDef:
    tree = ast.parse(src)
    node = tree.body[0]
    assert isinstance(node, ast.FunctionDef)
    return node


def _cls(src: str) -> ast.ClassDef:
    tree = ast.parse(src)
    node = tree.body[0]
    assert isinstance(node, ast.ClassDef)
    return node


# -- raises ----------------------------------------------------------


class TestExtractRaises:
    def test_single_raise(self) -> None:
        assert _extract_raises(_fn("def f():\n    raise ValueError('x')")) == ["ValueError"]

    def test_bare_raise_is_ignored(self) -> None:
        src = "def f():\n    try:\n        pass\n    except Exception:\n        raise"
        assert _extract_raises(_fn(src)) == []

    def test_multiple_exceptions_deduped_in_order(self) -> None:
        src = (
            "def f(x):\n"
            "    if x < 0:\n"
            "        raise ValueError('neg')\n"
            "    if x > 100:\n"
            "        raise ValueError('big')\n"
            "    raise TypeError('no')\n"
        )
        assert _extract_raises(_fn(src)) == ["ValueError", "TypeError"]

    def test_dotted_exception_name(self) -> None:
        src = "def f():\n    raise subprocess.TimeoutExpired('cmd', 1)"
        assert _extract_raises(_fn(src)) == ["subprocess.TimeoutExpired"]

    def test_exception_without_call(self) -> None:
        src = "def f():\n    raise StopIteration"
        assert _extract_raises(_fn(src)) == ["StopIteration"]

    def test_nested_function_raises_counted(self) -> None:
        src = "def f():\n" "    def inner():\n" "        raise RuntimeError('x')\n" "    inner()\n"
        # ast.walk descends into nested defs — the raise is part
        # of what `f` can propagate, so counting it is correct.
        assert _extract_raises(_fn(src)) == ["RuntimeError"]


# -- Literal values --------------------------------------------------


class TestExtractLiteralValues:
    def test_literal_tuple(self) -> None:
        ann = ast.parse("x: Literal['a', 'b', 'c']", mode="exec").body[0].annotation
        assert _extract_literal_values(ann) == ["a", "b", "c"]

    def test_literal_single_value(self) -> None:
        ann = ast.parse("x: Literal['only']", mode="exec").body[0].annotation
        assert _extract_literal_values(ann) == ["only"]

    def test_typing_qualified(self) -> None:
        ann = ast.parse("x: typing.Literal['a', 'b']", mode="exec").body[0].annotation
        assert _extract_literal_values(ann) == ["a", "b"]

    def test_non_literal_returns_none(self) -> None:
        ann = ast.parse("x: str", mode="exec").body[0].annotation
        assert _extract_literal_values(ann) is None

    def test_none_annotation_returns_none(self) -> None:
        assert _extract_literal_values(None) is None

    def test_int_literal_rejected(self) -> None:
        """Non-string literal members are intentionally skipped.

        Users ask about string enums (depths, doc_type, etc) —
        numeric literals are rare and muddy the rendered table.
        """
        ann = ast.parse("x: Literal[1, 2, 3]", mode="exec").body[0].annotation
        assert _extract_literal_values(ann) is None


class TestExtractParamLiterals:
    def test_mixed_params(self) -> None:
        node = _fn(
            "def f(depth: Literal['concept', 'task', 'reference'], name: str) -> None:\n    pass"
        )
        assert _extract_param_literals(node) == {
            "depth": ["concept", "task", "reference"],
        }

    def test_kwonly_literal(self) -> None:
        node = _fn("def f(*, mode: Literal['r', 'w']) -> None:\n    pass")
        assert _extract_param_literals(node) == {"mode": ["r", "w"]}

    def test_no_literal_params(self) -> None:
        node = _fn("def f(x: int, y: str) -> None:\n    pass")
        assert _extract_param_literals(node) == {}


# -- dataclass detection --------------------------------------------


class TestIsDataclass:
    def test_plain_decorator(self) -> None:
        assert _is_dataclass(_cls("@dataclass\nclass C:\n    x: int = 0")) is True

    def test_call_decorator(self) -> None:
        src = "@dataclass(frozen=True)\nclass C:\n    x: int = 0"
        assert _is_dataclass(_cls(src)) is True

    def test_qualified_decorator(self) -> None:
        src = "@dataclasses.dataclass\nclass C:\n    x: int = 0"
        assert _is_dataclass(_cls(src)) is True

    def test_qualified_call_decorator(self) -> None:
        src = "@dataclasses.dataclass(frozen=True)\nclass C:\n    x: int = 0"
        assert _is_dataclass(_cls(src)) is True

    def test_no_decorator(self) -> None:
        assert _is_dataclass(_cls("class C:\n    pass")) is False

    def test_unrelated_decorator(self) -> None:
        assert _is_dataclass(_cls("@property\nclass C:\n    pass")) is False


# -- dataclass fields ------------------------------------------------


class TestExtractDataclassFields:
    def test_fields_with_types_and_defaults(self) -> None:
        src = (
            "@dataclass\n"
            "class C:\n"
            "    name: str\n"
            "    count: int = 0\n"
            "    tags: list[str] = field(default_factory=list)\n"
        )
        assert _extract_dataclass_fields(_cls(src)) == [
            {"name": "name", "type": "str", "default": ""},
            {"name": "count", "type": "int", "default": "0"},
            {"name": "tags", "type": "list[str]", "default": "field(default_factory=list)"},
        ]

    def test_underscore_fields_skipped(self) -> None:
        src = "@dataclass\nclass C:\n    public: int = 0\n    _private: int = 0"
        assert _extract_dataclass_fields(_cls(src)) == [
            {"name": "public", "type": "int", "default": "0"},
        ]

    def test_empty_dataclass(self) -> None:
        src = "@dataclass\nclass C:\n    pass"
        assert _extract_dataclass_fields(_cls(src)) == []

    def test_plain_assignments_skipped(self) -> None:
        """Non-annotated class-level assignments are not fields."""
        src = "@dataclass\nclass C:\n    FOO = 1\n    bar: int = 0"
        assert _extract_dataclass_fields(_cls(src)) == [
            {"name": "bar", "type": "int", "default": "0"},
        ]
