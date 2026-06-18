"""Notebook-style aliases matching the vision document API."""

from __future__ import annotations

import re

from fopy.sorts import DEFAULT_SORT, Sort
from fopy.symbols import FuncSymbol, RelSymbol, Variable, symbols


def Vars(names: str, /, sort: Sort | str | None = None) -> Variable | tuple[Variable, ...]:
    """Create variables from a space-separated name list (vision-style ``Vars``)."""
    s = _coerce_sort(sort)
    parts = re.split(r"[\s,]+", names.strip())
    parts = [p for p in parts if p]
    if len(parts) == 1:
        return Variable(parts[0], s)
    return tuple(Variable(p, s) for p in parts)


def Function(name: str, arity: int, /, sort: Sort | str | None = None) -> FuncSymbol:
    """Return a function symbol factory (vision-style ``Function``)."""
    _ = _coerce_sort(sort)
    return FuncSymbol(name, arity)


def Relation(name: str, arity: int, /, sort: Sort | str | None = None) -> RelSymbol:
    """Return a relation symbol factory (vision-style ``Relation``)."""
    _ = _coerce_sort(sort)
    return RelSymbol(name, arity)


def _coerce_sort(sort: Sort | str | None) -> Sort:
    if sort is None:
        return DEFAULT_SORT
    if isinstance(sort, Sort):
        return sort
    return Sort(sort)


__all__ = ["Function", "Relation", "Vars", "symbols"]
