"""Variables and symbol factories."""

from __future__ import annotations

import re
from typing import cast

from fopy.core.basic import Basic
from fopy.sorts import DEFAULT_SORT, Sort

_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


def _subscript(n: int) -> str:
    if n < 0:
        return "₋" + "".join(_SUBSCRIPTS[int(c)] for c in str(-n))
    return "".join(_SUBSCRIPTS[int(c)] for c in str(n))


class Variable(Basic):
    """First-order variable, optionally typed by a :class:`~fopy.sorts.Sort`."""

    is_Term = True
    __slots__ = ("sort", "sym")

    def __new__(cls, sym: str, sort: Sort | None = None) -> Variable:
        """Allocate or intern a variable node."""
        from fopy.core.hashcons import hashcons_enabled, intern_basic
        from fopy.sorts import DEFAULT_SORT

        actual_sort = sort if sort is not None else DEFAULT_SORT
        if hashcons_enabled():
            return cast(Variable, intern_basic(cls, sym, actual_sort))
        return cast(Variable, super().__new__(cls))

    def __init__(self, sym: str, sort: Sort | None = None) -> None:
        """Create a variable with display symbol *sym* and optional sort (2nd arg)."""
        from fopy.sorts import DEFAULT_SORT

        super().__init__()
        self.sym = sym
        self.sort = sort if sort is not None else DEFAULT_SORT

    @classmethod
    def from_index(cls, i: int) -> Variable:
        """Build the standard indexed variable ``xᵢ`` for integer *i*."""
        return cls(f"x{_subscript(i)}")

    @property
    def args(self) -> tuple[str, Sort]:
        """Return ``(sym, sort)`` for hashing and structural equality."""
        return (self.sym, self.sort)

    def __repr__(self) -> str:
        if self.sort != DEFAULT_SORT:
            return f"{self.sym}:{self.sort.name}"
        return self.sym

    def __hash__(self) -> int:
        return hash((Variable, self.sym, self.sort))


class FuncSymbol:
    """Callable factory for function applications with fixed arity."""

    def __init__(self, name: str, arity: int) -> None:
        """Register function symbol *name* with the given *arity*."""
        self.name = name
        self.arity = arity

    def __call__(self, *args: Basic) -> Basic:
        """Apply *name* to *args*, raising if arity does not match."""
        from fopy.terms import Apply

        if len(args) != self.arity:
            raise ValueError(f"{self.name} expects arity {self.arity}, got {len(args)}")
        return Apply(self.name, args)


class RelSymbol:
    """Callable factory for relation atoms with fixed arity."""

    def __init__(self, name: str, arity: int) -> None:
        """Register relation symbol *name* with the given *arity*."""
        self.name = name
        self.arity = arity

    def __call__(self, *args: Basic) -> Basic:
        """Build an atom for *name* applied to *args*, checking arity."""
        from fopy.formulas import Atom
        from fopy.terms import Term

        if len(args) != self.arity:
            raise ValueError(f"{self.name} expects arity {self.arity}, got {len(args)}")
        return Atom(self.name, cast(tuple[Term, ...], args))


class ConstantSymbol(FuncSymbol):
    """Constant symbol (0-ary function)."""

    def __init__(self, name: str) -> None:
        """Register *name* as a zero-arity function symbol."""
        super().__init__(name, 0)


def symbols(names: str = "", /, *more: str) -> Variable | tuple[Variable, ...]:
    """Create variables from space- or comma-separated names."""
    if more:
        return tuple(Variable(n) for n in more)
    parts = re.split(r"[\s,]+", names.strip())
    parts = [p for p in parts if p]
    if len(parts) == 1:
        return Variable(parts[0])
    return tuple(Variable(p) for p in parts)
