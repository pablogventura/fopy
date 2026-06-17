"""Immutable base class for symbolic FO objects."""

from __future__ import annotations

from typing import Any, Iterator


class Basic:
    """Base for terms and formulas (SymPy-style)."""

    __slots__ = ("_mhash",)
    _mhash: int | None

    is_Term = False
    is_Formula = False

    def __new__(cls, *args: Any) -> Basic:
        obj = object.__new__(cls)
        obj._mhash = None
        return obj

    @property
    def args(self) -> tuple[Any, ...]:
        raise NotImplementedError

    def __hash__(self) -> int:
        if self._mhash is None:
            self._mhash = hash((type(self),) + self.args)
        return self._mhash

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        return self.args == other.args  # type: ignore[union-attr]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join(repr(a) for a in self.args)})"

    def walk(self) -> Iterator[Basic]:
        yield self
        for arg in self.args:
            if isinstance(arg, Basic):
                yield from arg.walk()
            elif isinstance(arg, (tuple, list, frozenset)):
                for item in arg:
                    if isinstance(item, Basic):
                        yield from item.walk()
