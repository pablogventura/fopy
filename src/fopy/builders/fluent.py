"""Fluent structure builder."""

from __future__ import annotations

from typing import Any

from fopy.signature import Signature
from fopy.structures import Structure


class StructureBuilder:
    def __init__(self, signature: Signature) -> None:
        self.signature = signature
        self._universe: list[Any] = []
        self._functions: dict[str, Any] = {}
        self._relations: dict[str, Any] = {}
        self._name = ""

    def universe(self, *elements: Any) -> StructureBuilder:
        self._universe = list(elements)
        return self

    def function(self, name: str, table: dict[tuple[Any, ...], Any]) -> StructureBuilder:
        self._functions[name] = table
        return self

    def relation(self, name: str, tuples: set[tuple[Any, ...]]) -> StructureBuilder:
        self._relations[name] = tuples
        return self

    def name(self, n: str) -> StructureBuilder:
        self._name = n
        return self

    def build(self) -> Structure:
        return Structure.from_tables(
            self.signature,
            self._universe,
            functions=self._functions,
            relations=self._relations,
            name=self._name,
        )


def build(signature: Signature) -> StructureBuilder:
    return StructureBuilder(signature)
