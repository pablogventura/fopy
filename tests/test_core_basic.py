"""Core Basic and visitor tests."""

from __future__ import annotations

import fopy as fo
from fopy.core.basic import Basic
from fopy.core.visitor import Visitor, transform, walk


def test_basic_equality():
    x1, x2 = fo.Variable("x"), fo.Variable("x")
    assert x1 == x2
    assert hash(x1) == hash(x2)


def test_basic_inequality():
    x, y = fo.Variable("x"), fo.Variable("y")
    assert x != y


def test_walk_includes_subterms():
    x, y = fo.symbols("x y")
    t = fo.Apply("f", (x, y))
    nodes = list(walk(t))
    assert len(nodes) >= 3


def test_walk_formula_quantifiers():
    x = fo.symbols("x")
    f = fo.forall(x, fo.Atom("P", (x,)))
    nodes = list(walk(f))
    assert len(nodes) >= 2


def test_transform_identity_on_atom():
    x = fo.symbols("x")
    a = fo.Atom("P", (x,))

    def ident(expr: Basic) -> Basic:
        return expr

    result = transform(a, ident)
    assert result.rel == "P"


class CollectVisitor(Visitor):
    def __init__(self) -> None:
        self.names: list[str] = []

    def visit_Atom(self, expr: fo.Atom) -> None:
        self.names.append(expr.rel)
        self.generic_visit(expr)


def test_visitor_dispatch_atom():
    x = fo.symbols("x")
    v = CollectVisitor()
    v.visit(fo.Atom("R", (x,)))
    assert v.names == ["R"]


def test_basic_repr():
    x = fo.Variable("x")
    assert "Variable" in repr(x) or "x" in repr(x)
