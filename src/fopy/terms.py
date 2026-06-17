"""First-order terms."""

from __future__ import annotations

from fopy.core.basic import Basic


class Term(Basic):
    is_Term = True


class Apply(Term):
    __slots__ = ("func", "_args")

    def __init__(self, func: str, args: tuple[Basic, ...]) -> None:
        super().__init__()
        self.func = func
        self._args = args

    @property
    def args(self) -> tuple:
        return (self.func,) + self._args

    def __repr__(self) -> str:
        inner = ", ".join(repr(a) for a in self._args)
        return f"{self.func}({inner})"


class Constant(Term):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    @property
    def args(self) -> tuple[str]:
        return (self.name,)

    def __repr__(self) -> str:
        return self.name
