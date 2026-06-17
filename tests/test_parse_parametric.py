"""Parametrized FO parser tests."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.parse import parse_formula
from fopy.parse.formula import parse_term


@pytest.mark.parametrize(
    "source",
    [
        "forall x P(x)",
        "exists x P(x)",
        "forall x exists y R(x,y)",
        "∀x ∃y R(x,y)",
        "P(x) & Q(x)",
        "P(x) | Q(x)",
        "P(x) -> Q(x)",
        "Q(x) <- P(x)",
        "P(x) <-> Q(x)",
        "~P(x)",
        "-P(x)",
        "(P(x) & Q(x)) | R(x)",
        "forall x (P(x) -> exists y R(x,y))",
        "x = y",
    ],
)
def test_parse_ok(source: str):
    f = parse_formula(
        source,
        funcs={"f": 1},
        rels={"P": 1, "Q": 1, "R": 2},
    )
    assert isinstance(f, fo.Formula)


@pytest.mark.parametrize(
    "source",
    [
        "forall x",
        "unknown atom",
        "P(x) &",
    ],
)
def test_parse_raises(source: str):
    with pytest.raises((ValueError, IndexError)):
        parse_formula(source, rels={"P": 1, "Q": 1, "R": 2})


def test_parse_term_constant_zero_ary():
    """Zero-ary functions use bare name as variable unless called with ()."""
    t = parse_term("c", funcs={"c": 0}, vars_map={})
    assert isinstance(t, fo.Variable)


def test_parse_term_function_zero_ary():
    t = parse_term("c()", funcs={"c": 0}, vars_map={})
    assert isinstance(t, fo.Constant)


def test_parse_term_nested():
    t = parse_term("f(g(x))", funcs={"f": 1, "g": 1})
    assert isinstance(t, fo.Apply)
    s = "forall x exists y R(x,y) -> P(y)"
    f = parse_formula(s, rels={"R": 2, "P": 1})
    text = fo.sstr(f)
    assert "forall" in text
