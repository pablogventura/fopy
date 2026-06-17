"""Formula construction and parsing tests."""

import fopy as fo
from fopy.parse import parse_formula


def test_formula_constructors():
    x, y = fo.symbols("x y")
    a = fo.Atom("R", (x, y))
    b = fo.eq(x, y)
    c = a & b
    assert isinstance(c, fo.And)


def test_parse_formula():
    f = parse_formula("forall x exists y R(x,y)", rels={"R": 2})
    assert isinstance(f, fo.ForAll)


def test_parse_equality():
    f = parse_formula("x = y")
    assert isinstance(f, fo.Eq)


def test_negation_idempotent():
    x = fo.symbols("x")
    f = ~~fo.Atom("P", (x,))
    assert fo.simplify(f) == fo.Atom("P", (x,))
