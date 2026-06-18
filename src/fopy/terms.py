"""First-order terms."""

from __future__ import annotations

from typing import cast

from fopy.core.basic import Basic


class Term(Basic):
    """Base class for first-order terms."""

    is_Term = True


class Apply(Term):
    """Function application term ``func(arg₁, …, argₙ)``."""

    __slots__ = ("_args", "func")

    def __new__(cls, func: str, args: tuple[Basic, ...]) -> Apply:
        """Allocate or intern an application node."""
        from fopy.core.hashcons import hashcons_enabled, intern_basic

        if hashcons_enabled():
            return cast(Apply, intern_basic(cls, func, args))
        return cast(Apply, super().__new__(cls))

    def __init__(self, func: str, args: tuple[Basic, ...]) -> None:
        """Apply function symbol *func* to argument terms *args*."""
        super().__init__()
        self.func = func
        self._args = args

    @property
    def args(self) -> tuple:
        """Return ``(func,) + argument tuple``."""
        return (self.func,) + self._args

    def __repr__(self) -> str:
        inner = ", ".join(repr(a) for a in self._args)
        return f"{self.func}({inner})"


class Constant(Term):
    """Nullary constant symbol represented as a term."""

    __slots__ = ("name",)

    def __new__(cls, name: str) -> Constant:
        """Allocate or intern a constant node."""
        from fopy.core.hashcons import hashcons_enabled, intern_basic

        if hashcons_enabled():
            return cast(Constant, intern_basic(cls, name))
        return cast(Constant, super().__new__(cls))

    def __init__(self, name: str) -> None:
        """Create the constant named *name*."""
        super().__init__()
        self.name = name

    @property
    def args(self) -> tuple[str]:
        """Return ``(name,)``."""
        return (self.name,)

    def __repr__(self) -> str:
        return self.name
