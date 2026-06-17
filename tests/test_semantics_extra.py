"""Extended semantics and printing coverage."""

import fopy as fo
from fopy.formulas import And, ForAll, Not, Or
from fopy.semantics import satisfy


def test_forall_false():
    s = fo.builders.chain(2)
    x = fo.symbols("x")
    leq = fo.RelSymbol("leq", 2)
    f = fo.forall(x, leq(x, x))
    assert satisfy(f, s, {})


def test_exists_true():
    s = fo.builders.chain(3)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    f = fo.exists(x, fo.exists(y, leq(x, y) & ~leq(y, x)))
    assert satisfy(f, s, {})


def test_or_and_semantics():
    s = fo.builders.chain(2)
    x = fo.symbols("x")
    P = fo.RelSymbol("leq", 2)
    a = P(x, x)
    b = ~a
    assert satisfy(Or(frozenset({a, b})), s, {x: 0})
    assert not satisfy(And(frozenset({a, b})), s, {x: 0})


def test_not_forall():
    s = fo.builders.chain(2)
    x, y = fo.symbols("x y")
    leq = fo.RelSymbol("leq", 2)
    f = Not(ForAll(x, ForAll(y, leq(x, y))))
    assert satisfy(f, s, {})


def test_pprint_long_formula():
    x, y, z = fo.symbols("x y z")
    f = fo.forall(x, fo.exists(y, fo.exists(z, fo.eq(x, y) & fo.eq(y, z))))
    text = fo.pprint(f)
    assert "forall" in text


def test_constant_symbol():
    c = fo.ConstantSymbol("c")
    assert c.arity == 0
