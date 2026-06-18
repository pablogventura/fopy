"""Visitor utilities for FO expression trees."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from fopy.core.basic import Basic


class Visitor:
    """SymPy-style visitor over :class:`~fopy.core.basic.Basic` trees.

    Subclass and override ``visit_<ClassName>`` methods; unhandled node types
    fall back to :meth:`generic_visit`.
    """

    def visit(self, expr: Basic) -> Any:
        """Dispatch to ``visit_<ClassName>`` or :meth:`generic_visit`."""
        method = getattr(self, f"visit_{type(expr).__name__}", self.generic_visit)
        return method(expr)

    def generic_visit(self, expr: Basic) -> Any:
        """Recursively visit children without transforming the root."""
        for arg in expr.args:
            if isinstance(arg, Basic):
                self.visit(arg)
            elif isinstance(arg, (frozenset, tuple)):
                for item in arg:
                    if isinstance(item, Basic):
                        self.visit(item)
        return None


def walk(expr: Basic) -> Iterator[Basic]:
    """Yield all sub-expressions of *expr* in preorder.

    Args:
        expr: Root of the expression tree.

    Yields:
        Each :class:`~fopy.core.basic.Basic` node reachable from *expr*.
    """
    yield from expr.walk()


def transform(expr: Basic, fn: Callable[[Basic], Basic]) -> Basic:
    """Apply *fn* bottom-up after recursively rebuilding children.

    Args:
        expr: Root expression to transform.
        fn: Callable invoked on each rebuilt node (including the root).

    Returns:
        Transformed expression tree.
    """
    new_args: list[Any] = []
    for arg in expr.args:
        if isinstance(arg, Basic):
            new_args.append(transform(arg, fn))
        elif isinstance(arg, frozenset):
            new_args.append(frozenset(transform(x, fn) for x in arg))
        elif isinstance(arg, tuple):
            new_args.append(tuple(transform(x, fn) if isinstance(x, Basic) else x for x in arg))
        else:
            new_args.append(arg)
    rebuilt = type(expr)(*new_args)
    return fn(rebuilt)
