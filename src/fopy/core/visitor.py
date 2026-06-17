"""Visitor utilities for FO expression trees."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from fopy.core.basic import Basic

T = TypeVar("T")


class Visitor:
    """SymPy-style visitor over :class:`~fopy.core.basic.Basic` trees."""

    def visit(self, expr: Basic) -> Any:
        method = getattr(self, f"visit_{type(expr).__name__}", self.generic_visit)
        return method(expr)

    def generic_visit(self, expr: Basic) -> Any:
        for arg in expr.args:
            if isinstance(arg, Basic):
                self.visit(arg)
            elif isinstance(arg, frozenset):
                for item in arg:
                    if isinstance(item, Basic):
                        self.visit(item)
            elif isinstance(arg, tuple):
                for item in arg:
                    if isinstance(item, Basic):
                        self.visit(item)
        return None


def walk(expr: Basic):
    """Yield all sub-expressions in preorder."""
    yield from expr.walk()


def transform(expr: Basic, fn: Callable[[Basic], Basic]) -> Basic:
    """Bottom-up transform."""
    new_args = []
    for arg in expr.args:
        if isinstance(arg, Basic):
            new_args.append(transform(arg, fn))
        elif isinstance(arg, frozenset):
            new_args.append(frozenset(transform(x, fn) for x in arg))
        elif isinstance(arg, tuple):
            new_args.append(tuple(transform(x, fn) if isinstance(x, Basic) else x for x in arg))
        else:
            new_args.append(arg)
    rebuilt = type(expr)(*new_args)  # type: ignore[misc, call-arg]
    return fn(rebuilt)
