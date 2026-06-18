"""Finite structures (models)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from fopy.signature import Signature
from fopy.sorts import DEFAULT_SORT, Sort

Interpretation = Callable[..., Any] | dict[tuple[Any, ...], Any] | set[tuple[Any, ...]]


@dataclass
class Structure:
    """First-order structure over a finite universe."""

    signature: Signature
    universe: list[Any]
    functions: dict[str, Interpretation] = field(default_factory=dict)
    relations: dict[str, Interpretation] = field(default_factory=dict)
    name: str = ""
    universes: dict[str, list[Any]] | None = None

    def __post_init__(self) -> None:
        for f, arity in self.signature.functions.items():
            if f not in self.functions:
                raise ValueError(f"Missing interpretation for function {f}")
            if arity == 0:
                continue
        for r, _arity in self.signature.relations.items():
            if r not in self.relations:
                raise ValueError(f"Missing interpretation for relation {r}")

    @classmethod
    def from_tables(
        cls,
        signature: Signature,
        universe: list[Any],
        functions: dict[str, dict[tuple[Any, ...], Any] | Any] | None = None,
        relations: Mapping[str, set[tuple[Any, ...]] | dict[tuple[Any, ...], bool]] | None = None,
        name: str = "",
        universes: dict[str, list[Any]] | None = None,
    ) -> Structure:
        """Construct a structure from explicit function and relation tables.

        Args:
            signature: Language signature for the structure.
            universe: Ordered list of universe elements.
            functions: Map from function symbols to Cayley tables or constant values.
            relations: Map from relation symbols to extension sets or truth tables.
            name: Optional human-readable structure name.
            universes: Optional many-sorted carriers keyed by sort name.

        Returns:
            :class:`Structure` with the given tables.

        Raises:
            KeyError: If a symbol in *signature* lacks an interpretation.
        """
        functions = functions or {}
        relations = dict(relations or {})
        fn_interp: dict[str, Interpretation] = {}
        for sym, arity in signature.functions.items():
            if sym not in functions:
                raise KeyError(sym)
            data = functions[sym]
            if arity == 0:
                fn_interp[sym] = data
            else:
                fn_interp[sym] = dict(data)

        rel_interp: dict[str, Interpretation] = {}
        for sym, arity in signature.relations.items():
            if sym not in relations:
                raise KeyError(sym)
            data = relations[sym]
            if isinstance(data, set):
                rel_interp[sym] = data
            else:

                def make_rel(
                    d: dict[tuple[Any, ...], bool] = data,
                    _a: int = arity,
                ) -> Callable[..., bool]:
                    """Wrap a truth table dict as a variadic relation callable."""

                    def rel(*args: Any) -> bool:
                        """Return whether tuple *args* is in the relation."""

                        return bool(d.get(args, False))

                    return rel

                rel_interp[sym] = make_rel()

        return cls(signature, list(universe), fn_interp, rel_interp, name, universes)

    def universe_for(self, sort: Sort | str = DEFAULT_SORT) -> list[Any]:
        """Return the carrier for *sort* (many-sorted lite).

        When :attr:`universes` is set, named sorts map to their carriers; the
        default sort ``U`` and unknown names fall back to :attr:`universe`.
        """
        if self.universes:
            key = sort.name if isinstance(sort, Sort) else sort
            if key in self.universes:
                return list(self.universes[key])
        return self.universe

    def call_function(self, name: str, args: tuple[Any, ...]) -> Any:
        """Apply the interpretation of function symbol *name* to *args*.

        Args:
            name: Function symbol.
            args: Tuple of arguments drawn from the universe.

        Returns:
            Value of the function on *args*.
        """
        interp = self.functions[name]
        if callable(interp) and not isinstance(interp, dict):
            return interp(*args)
        if isinstance(interp, dict):
            return interp[args]
        return interp

    def call_relation(self, name: str, args: tuple[Any, ...]) -> bool:
        """Test whether relation symbol *name* holds on *args*.

        Args:
            name: Relation symbol.
            args: Tuple of arguments drawn from the universe.

        Returns:
            Truth value of the relation on *args*.
        """
        interp = self.relations[name]
        if isinstance(interp, set):
            return args in interp
        if isinstance(interp, dict):
            return bool(interp.get(args, False))
        return bool(interp(*args))

    def satisfies(self, formula: object) -> bool:
        """Return whether this structure satisfies a closed formula.

        Args:
            formula: Closed :class:`~fopy.formulas.Formula` to test.

        Returns:
            ``True`` if *formula* holds in ``self``.

        Raises:
            TypeError: If *formula* is not a :class:`~fopy.formulas.Formula`.
        """
        from fopy.formulas import Formula
        from fopy.semantics import satisfy

        if not isinstance(formula, Formula):
            raise TypeError("formula must be a fopy Formula")
        return satisfy(formula, self, {})
