"""Variables and symbol factories."""

from __future__ import annotations

import re
from typing import overload

from fopy.core.basic import Basic

_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


def _subscript(n: int) -> str:
    if n < 0:
        return "₋" + "".join(_SUBSCRIPTS[int(c)] for c in str(-n))
    return "".join(_SUBSCRIPTS[int(c)] for c in str(n))


class Variable(Basic):
    """First-order variable."""

    is_Term = True
    __slots__ = ("sym",)

    def __init__(self, sym: str) -> None:
        super().__init__()
        self.sym = sym

    @classmethod
    def from_index(cls, i: int) -> Variable:
        return cls(f"x{_subscript(i)}")

    @property
    def args(self) -> tuple[str]:
        return (self.sym,)

    def __repr__(self) -> str:
        return self.sym

    def __hash__(self) -> int:
        return hash((Variable, self.sym))


class FuncSymbol:
    def __init__(self, name: str, arity: int) -> None:
        self.name = name
        self.arity = arity

    def __call__(self, *args: Basic):
        from fopy.terms import Apply

        if len(args) != self.arity:
            raise ValueError(f"{self.name} expects arity {self.arity}, got {len(args)}")
        return Apply(self.name, args)


class RelSymbol:
    def __init__(self, name: str, arity: int) -> None:
        self.name = name
        self.arity = arity

    def __call__(self, *args: Basic):
        from fopy.formulas import Atom

        if len(args) != self.arity:
            raise ValueError(f"{self.name} expects arity {self.arity}, got {len(args)}")
        return Atom(self.name, args)


class ConstantSymbol(FuncSymbol):
    """Constant symbol (0-ary function)."""

    def __init__(self, name: str) -> None:
        super().__init__(name, 0)


@overload
def symbols(names: str) -> Variable | tuple[Variable, ...]: ...


@overload
def symbols(*names: str) -> tuple[Variable, ...]: ...


def symbols(names: str = "", /, *more: str) -> Variable | tuple[Variable, ...]:
    """Create variables from space- or comma-separated names."""
    if more:
        return tuple(Variable(n) for n in more)
    parts = re.split(r"[\s,]+", names.strip())
    parts = [p for p in parts if p]
    if len(parts) == 1:
        return Variable(parts[0])
    return tuple(Variable(p) for p in parts)
