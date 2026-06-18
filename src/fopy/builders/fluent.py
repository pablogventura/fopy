"""Fluent structure builder."""

from __future__ import annotations

from typing import Any

from fopy.signature import Signature
from fopy.structures import Structure


class StructureBuilder:
    """Fluent builder for :class:`~fopy.structures.Structure` instances."""

    def __init__(self, signature: Signature) -> None:
        """Create a builder for structures over *signature*.

        Args:
            signature: Language signature of the structure to build.
        """
        self.signature = signature
        self._universe: list[Any] = []
        self._functions: dict[str, Any] = {}
        self._relations: dict[str, Any] = {}
        self._name = ""

    def universe(self, *elements: Any) -> StructureBuilder:
        """Set the universe elements.

        Args:
            *elements: Universe elements in display order.

        Returns:
            ``self`` for method chaining.
        """
        self._universe = list(elements)
        return self

    def function(self, name: str, table: dict[tuple[Any, ...], Any]) -> StructureBuilder:
        """Register a function interpretation table.

        Args:
            name: Function symbol from the signature.
            table: Cayley table mapping argument tuples to values.

        Returns:
            ``self`` for method chaining.
        """
        self._functions[name] = table
        return self

    def relation(self, name: str, tuples: set[tuple[Any, ...]]) -> StructureBuilder:
        """Register a relation as an extension set.

        Args:
            name: Relation symbol from the signature.
            tuples: Set of argument tuples where the relation holds.

        Returns:
            ``self`` for method chaining.
        """
        self._relations[name] = tuples
        return self

    def name(self, n: str) -> StructureBuilder:
        """Set an optional display name for the structure.

        Args:
            n: Human-readable structure name.

        Returns:
            ``self`` for method chaining.
        """
        self._name = n
        return self

    def build(self) -> Structure:
        """Materialize the configured structure.

        Returns:
            :class:`~fopy.structures.Structure` built from accumulated tables.
        """
        return Structure.from_tables(
            self.signature,
            self._universe,
            functions=self._functions,
            relations=self._relations,
            name=self._name,
        )


def build(signature: Signature) -> StructureBuilder:
    """Start a fluent builder for structures over *signature*.

    Args:
        signature: Language signature of the structure to build.

    Returns:
        New :class:`StructureBuilder` instance.
    """
    return StructureBuilder(signature)
