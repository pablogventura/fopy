"""Exhaustive printing tests for str, latex, pretty."""

from __future__ import annotations

import pytest

import fopy as fo


@pytest.fixture
def sample_formulas():
    x, y, z = fo.symbols("x y z")
    P = fo.RelSymbol("P", 1)
    Q = fo.RelSymbol("Q", 1)
    R = fo.RelSymbol("R", 2)
    return {
        "atom": P(x),
        "eq": fo.eq(x, y),
        "and": P(x) & Q(x),
        "or": P(x) | Q(x),
        "not": ~P(x),
        "forall": fo.forall(x, P(x)),
        "exists": fo.exists(y, R(x, y)),
        "impl": P(x) >> Q(x),
        "true": fo.true_formula(),
        "false": fo.false_formula(),
        "nested": fo.forall(
            x,
            fo.exists(y, P(x) & Q(y) & fo.eq(x, z)),
        ),
    }


@pytest.mark.parametrize(
    "key", ["atom", "eq", "and", "or", "not", "forall", "exists", "impl", "true", "false"]
)
def test_sstr_all(sample_formulas, key: str):
    text = fo.sstr(sample_formulas[key])
    assert isinstance(text, str)
    assert len(text) > 0


@pytest.mark.parametrize("key", ["atom", "eq", "and", "or", "not", "forall", "exists"])
def test_latex_all(sample_formulas, key: str):
    text = fo.latex(sample_formulas[key])
    assert isinstance(text, str)
    assert len(text) > 0


def test_latex_subscript_indices():
    for i in range(5):
        v = fo.Variable.from_index(i)
        assert "x" in fo.latex(v)


def test_pprint_short_formula(sample_formulas):
    assert fo.pprint(sample_formulas["atom"]) == fo.sstr(sample_formulas["atom"])


def test_pprint_long_forall():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(
        x,
        fo.exists(y, fo.eq(x, y) & fo.eq(y, z) & fo.Atom("P", (x,))),
    )
    text = fo.pprint(f)
    assert "forall" in text


def test_pprint_not_multiline():
    x = fo.symbols("x")
    f = ~fo.forall(x, fo.Atom("Q", (x,)))
    text = fo.pprint(f)
    assert "~" in text or "forall" in text


def test_sstr_term_apply():
    x, y = fo.symbols("x y")
    t = fo.Apply("f", (x, y))
    assert "f(" in fo.sstr(t)


def test_sstr_constant():
    assert fo.sstr(fo.Constant("a")) == "a"
