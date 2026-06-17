"""Finite structures (models)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from fopy.signature import Signature


Interpretation = Callable[..., Any] | dict[tuple[Any, ...], Any]


@dataclass
class Structure:
    """First-order structure over a finite universe."""

    signature: Signature
    universe: list[Any]
    functions: dict[str, Interpretation] = field(default_factory=dict)
    relations: dict[str, Interpretation] = field(default_factory=dict)
    name: str = ""

    def __post_init__(self) -> None:
        for f, arity in self.signature.functions.items():
            if f not in self.functions:
                raise ValueError(f"Missing interpretation for function {f}")
            if arity == 0:
                continue
        for r, arity in self.signature.relations.items():
            if r not in self.relations:
                raise ValueError(f"Missing interpretation for relation {r}")

    @classmethod
    def from_tables(
        cls,
        signature: Signature,
        universe: list[Any],
        functions: dict[str, dict[tuple[Any, ...], Any] | Any] | None = None,
        relations: dict[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]] | None = None,
        name: str = "",
    ) -> Structure:
        functions = functions or {}
        relations = relations or {}
        fn_interp: dict[str, Interpretation] = {}
        for sym, arity in signature.functions.items():
            if sym not in functions:
                raise KeyError(sym)
            data = functions[sym]
            if arity == 0:
                fn_interp[sym] = data  # type: ignore[assignment]
            else:
                fn_interp[sym] = dict(data)  # type: ignore[arg-type]

        rel_interp: dict[str, Interpretation] = {}
        for sym, arity in signature.relations.items():
            if sym not in relations:
                raise KeyError(sym)
            data = relations[sym]
            if isinstance(data, set):
                rel_interp[sym] = data
            else:

                def make_rel(d=data, a=arity):
                    def rel(*args: Any) -> bool:
                        return bool(d.get(args, False))

                    return rel

                rel_interp[sym] = make_rel()

        return cls(signature, list(universe), fn_interp, rel_interp, name)

    def call_function(self, name: str, args: tuple[Any, ...]) -> Any:
        interp = self.functions[name]
        if callable(interp) and not isinstance(interp, dict):
            return interp(*args)
        if isinstance(interp, dict):
            return interp[args]
        return interp

    def call_relation(self, name: str, args: tuple[Any, ...]) -> bool:
        interp = self.relations[name]
        if isinstance(interp, set):
            return args in interp
        if isinstance(interp, dict):
            return bool(interp.get(args, False))
        return bool(interp(*args))

    def satisfies(self, formula: object) -> bool:
        """True if this structure satisfies a closed formula."""
        from fopy.formulas import Formula
        from fopy.semantics import satisfy

        if not isinstance(formula, Formula):
            raise TypeError("formula must be a fopy Formula")
        return satisfy(formula, self, {})
