"""Open formulas layer extra tests."""

from fopy.finite.open_formulas import (
    Term,
    Variable,
    and_formula,
    false_formula,
    neg,
    or_formula,
    true_formula,
)
from fopy.finite.relops import Operation


def test_term_str_and_grade():
    x = Variable.new("x")
    t = Term.from_variable(x)
    assert t.grade() == 0
    op = Operation.new("f", 2)
    op.add([0, 0, 0])
    t2 = Term.op_term(
        __import__("fopy.finite.open_formulas", fromlist=["OpSym"]).OpSym.new("f", 2), [t, t]
    )
    assert t2.grade() == 1


def test_formula_true_false():
    x = Variable.new("x")
    t = true_formula({x})
    f = false_formula({x})
    assert "⊤" in str(t)
    assert "⊥" in str(f)


def test_formula_neg_double():
    x = Variable.new("x")
    y = Variable.new("y")
    t1 = Term.from_variable(x)
    t2 = Term.from_variable(y)
    from fopy.finite.open_formulas import eq

    inner = eq(t1, t2)
    f = neg(neg(inner))
    assert f == inner


def test_and_or_merge():
    x = Variable.new("x")
    t = Term.from_variable(x)
    from fopy.finite.open_formulas import eq

    a = eq(t, t)
    b = eq(t, t)
    c = and_formula(a, b)
    d = or_formula(a, b)
    assert c.kind.name == "AND" or c == a
    assert d.kind.name == "OR" or d == a
