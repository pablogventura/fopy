"""First-order signatures."""

from __future__ import annotations

from dataclasses import dataclass, field

from fopy.sorts import DEFAULT_SORT, Sort


@dataclass(frozen=True)
class Signature:
    """Language signature: function and relation symbols with arities.

    Many-sorted lite: optional ``sorts`` names extra sorts; symbols without an
    explicit entry use :data:`~fopy.sorts.DEFAULT_SORT` (``U``).
    """

    functions: dict[str, int] = field(default_factory=dict)
    relations: dict[str, int] = field(default_factory=dict)
    sorts: tuple[Sort, ...] = (DEFAULT_SORT,)
    function_sorts: dict[str, tuple[Sort, ...]] = field(default_factory=dict)
    relation_sorts: dict[str, tuple[Sort, ...]] = field(default_factory=dict)

    def function(self, name: str) -> str:
        """Validate and return a function symbol from the signature.

        Args:
            name: Function symbol to look up.

        Returns:
            *name* unchanged when present in :attr:`functions`.

        Raises:
            KeyError: If *name* is not a function symbol.
        """
        if name not in self.functions:
            raise KeyError(f"Unknown function symbol: {name}")
        return name

    def relation(self, name: str) -> str:
        """Validate and return a relation symbol from the signature.

        Args:
            name: Relation symbol to look up.

        Returns:
            *name* unchanged when present in :attr:`relations`.

        Raises:
            KeyError: If *name* is not a relation symbol.
        """
        if name not in self.relations:
            raise KeyError(f"Unknown relation symbol: {name}")
        return name

    def constant(self, name: str) -> str:
        """Validate and return a constant (nullary function) symbol.

        Args:
            name: Constant symbol to look up.

        Returns:
            *name* unchanged when present with arity ``0``.

        Raises:
            KeyError: If *name* is not a constant symbol.
        """
        if self.functions.get(name, -1) != 0:
            raise KeyError(f"Unknown constant symbol: {name}")
        return name

    def subtype(
        self,
        functions: list[str] | None = None,
        relations: list[str] | None = None,
    ) -> Signature:
        """Restrict the signature to selected symbols.

        Args:
            functions: Function symbols to retain; defaults to none.
            relations: Relation symbols to retain; defaults to none.

        Returns:
            New :class:`Signature` containing only the listed symbols.
        """
        functions = functions or []
        relations = relations or []
        return Signature(
            functions={f: self.functions[f] for f in functions},
            relations={r: self.relations[r] for r in relations},
        )

    def __add__(self, other: Signature) -> Signature:
        """Merge two signatures, with *other* overriding on symbol clash.

        Args:
            other: Signature whose symbols are added to ``self``.

        Returns:
            Combined signature.
        """
        merged_f = dict(self.functions)
        merged_f.update(other.functions)
        merged_r = dict(self.relations)
        merged_r.update(other.relations)
        return Signature(functions=merged_f, relations=merged_r)

    def __sub__(self, other: Signature) -> Signature:
        """Remove symbols present in *other* from ``self``.

        Args:
            other: Signature whose symbols are subtracted.

        Returns:
            Signature containing symbols in ``self`` but not in *other*.
        """
        return Signature(
            functions={k: v for k, v in self.functions.items() if k not in other.functions},
            relations={k: v for k, v in self.relations.items() if k not in other.relations},
        )

    def is_subtype_of(self, other: Signature) -> bool:
        """Return whether every symbol of ``self`` appears in *other* with the same arity.

        Args:
            other: Candidate super-signature.

        Returns:
            ``True`` if ``self`` is a sub-signature of *other*.
        """
        return all(
            k in other.functions and self.functions[k] == other.functions[k] for k in self.functions
        ) and all(
            k in other.relations and self.relations[k] == other.relations[k] for k in self.relations
        )
