"""Finite relational operations and relations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fopy.finite.preprocessing import Pattern


@dataclass
class Relation:
    sym: str
    arity: int
    r: set[tuple[int, ...]] = field(default_factory=set)
    pattern: Pattern | None = None
    superrel_sym: str | None = None
    superrel: Relation | None = None

    @classmethod
    def new(cls, sym: str, arity: int) -> Relation:
        return cls(sym=sym, arity=arity)

    def with_tuples(self, tuples: list[list[int]] | list[tuple[int, ...]]) -> Relation:
        for t in tuples:
            row = tuple(t)
            if len(row) == self.arity:
                self.r.add(row)
        return self

    def add(self, t: list[int] | tuple[int, ...]) -> None:
        row = tuple(t)
        if len(row) == self.arity:
            self.r.add(row)

    def contains(self, args: list[int] | tuple[int, ...]) -> bool:
        return tuple(args) in self.r

    def restrict(self, subuniverse: set[int]) -> Relation:
        result = Relation.new(self.sym, self.arity)
        for t in self.r:
            if all(x in subuniverse for x in t):
                result.add(t)
        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relation):
            return NotImplemented
        return self.sym == other.sym and self.r == other.r

    def __hash__(self) -> int:
        h = hash(self.sym)
        for t in sorted(self.r):
            for x in t:
                h ^= hash(x)
        return h


@dataclass
class Operation:
    sym: str
    arity: int
    op: dict[tuple[int, ...], int] = field(default_factory=dict)

    @classmethod
    def new(cls, sym: str, arity: int) -> Operation:
        return cls(sym=sym, arity=arity)

    def add(self, t: list[int] | tuple[int, ...]) -> None:
        row = list(t)
        if len(row) >= self.arity + 1:
            args = tuple(row[: self.arity])
            result = row[self.arity]
            self.op[args] = result

    def call(self, args: list[int] | tuple[int, ...]) -> int | None:
        row = tuple(args)
        if len(row) == self.arity:
            return self.op.get(row)
        return None

    def restrict(self, subuniverse: set[int]) -> Operation:
        result = Operation.new(self.sym, self.arity)
        for t, v in self.op.items():
            if all(x in subuniverse for x in t) and v in subuniverse:
                result.add(list(t) + [v])
        return result
