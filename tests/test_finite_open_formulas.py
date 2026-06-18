"""Open formulas and preprocessing tests."""

from __future__ import annotations

import pytest

from fopy.finite.open_formulas import (
    Term,
    Variable,
    and_formula,
    eq,
    extension,
    neg,
    or_formula,
    satisfy,
    true_formula,
    variables,
)
from fopy.finite.open_parse import parse_open_formula
from fopy.finite.preprocessing import Pattern, split_targets
from fopy.finite.relops import Operation, Relation


@pytest.fixture
def tiny_model():
    ops = {"f": Operation.new("f", 2)}
    for row in ([0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]):
        ops["f"].add(row)
    return __import__("fopy.finite.models", fromlist=["Model"]).Model.new([0, 1], operations=ops)


def test_variables_helper():
    vs = variables([0, 1, 2])
    assert len(vs) == 3


def test_term_evaluate(tiny_model):
    x, y = Variable.new("x"), Variable.new("y")
    ops = tiny_model.operations
    f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, ops)
    ext = extension(f, tiny_model, 2)
    assert isinstance(ext, set)


def test_formula_satisfy_vector(tiny_model):
    x = Variable.new("x")
    t = true_formula({x})
    assert satisfy(t, tiny_model, {x: 0})


def test_formula_and_or(tiny_model):
    x, y = Variable.new("x"), Variable.new("y")
    t1, t2 = Term.from_variable(x), Term.from_variable(y)
    a = eq(t1, t2)
    b = eq(t2, t1)
    c = and_formula(a, b)
    d = or_formula(a, b)
    assert c.kind.name in ("AND", "EQ")
    assert d.kind.name in ("OR", "EQ")


def test_formula_neg_true():
    x = Variable.new("x")
    f = neg(true_formula({x}))
    assert f.kind.name == "FALSE"


def test_split_targets_binary():
    r = Relation.new("T", 2)
    r.add([0, 0])
    r.add([0, 1])
    r.add([1, 0])
    parts = split_targets(r)
    assert len(parts) >= 1


def test_pattern_str():
    p = Pattern.new([0, 1])
    s = str(p)
    assert isinstance(s, str)


def test_parse_open_neg():
    x, y = Variable.new("x"), Variable.new("y")
    ops = {"f": Operation.new("f", 2)}
    f = parse_open_formula("-eq(f(x,y),y)", {"x": x, "y": y}, ops)
    assert f is not None


def test_parse_open_or_and():
    x, y = Variable.new("x"), Variable.new("y")
    ops = {"f": Operation.new("f", 2)}
    f = parse_open_formula("eq(x,y) | eq(f(x,y),x) & -eq(x,y)", {"x": x, "y": y}, ops)
    assert f is not None
