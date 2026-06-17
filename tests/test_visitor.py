"""Visitor and core walk tests."""

import fopy as fo
from fopy.core.basic import Basic
from fopy.core.visitor import Visitor, walk


class CountVisitor(Visitor):
    def __init__(self) -> None:
        self.count = 0

    def generic_visit(self, expr: Basic) -> None:
        self.count += 1
        return super().generic_visit(expr)


def test_walk_formula():
    x = fo.symbols("x")
    f = fo.forall(x, fo.Atom("P", (x,)))
    nodes = list(walk(f))
    assert len(nodes) >= 2


def test_visitor_counts():
    x, y = fo.symbols("x y")
    f = fo.eq(x, y) & fo.Atom("R", (x, y))
    v = CountVisitor()
    v.visit(f)
    assert v.count >= 3
