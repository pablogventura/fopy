"""Immutable base class for symbolic FO objects."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


class Basic:
    """Immutable base class for symbolic first-order terms and formulas.

    Subclasses expose structural ``args``, support hashing/equality by shape,
    and provide :meth:`walk` for preorder traversal (SymPy-style).
    """

    __slots__ = ("_mhash",)
    _mhash: int | None

    is_Term = False
    is_Formula = False

    def __new__(cls, *args: Any) -> Basic:
        """Allocate an instance with an uninitialized hash cache."""
        obj = object.__new__(cls)
        obj._mhash = None
        return obj

    @property
    def args(self) -> tuple[Any, ...]:
        """Structural children of this node (subclasses must implement)."""
        raise NotImplementedError

    def __hash__(self) -> int:
        """Hash based on node type and :attr:`args`, cached after first use."""
        if self._mhash is None:
            self._mhash = hash((type(self),) + self.args)
        return self._mhash

    def __eq__(self, other: object) -> bool:
        """Structural equality for nodes of the same concrete type."""
        if type(self) is not type(other):
            return False
        assert isinstance(other, Basic)
        return self.args == other.args

    def __repr__(self) -> str:
        """Debug representation ``ClassName(arg1, arg2, ...)``."""
        return f"{type(self).__name__}({', '.join(repr(a) for a in self.args)})"

    def walk(self) -> Iterator[Basic]:
        """Yield this node and all nested :class:`Basic` sub-expressions in preorder."""
        yield self
        for arg in self.args:
            if isinstance(arg, Basic):
                yield from arg.walk()
            elif isinstance(arg, (tuple, list, frozenset)):
                for item in arg:
                    if isinstance(item, Basic):
                        yield from item.walk()
