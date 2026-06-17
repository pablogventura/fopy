"""Named universe elements."""

from __future__ import annotations

from typing import Any, Hashable, Iterator


class Domain:
    """Ordered collection of structure elements with optional attribute access."""

    def __init__(self, *elements: Hashable) -> None:
        self._elements = list(elements)
        self._index = {e: i for i, e in enumerate(self._elements)}

    def __iter__(self) -> Iterator[Any]:
        return iter(self._elements)

    def __len__(self) -> int:
        return len(self._elements)

    def __getitem__(self, idx: int | str) -> Any:
        if isinstance(idx, int):
            return self._elements[idx]
        return getattr(self, idx)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._index:
            return name
        raise AttributeError(name)

    def list(self) -> list[Any]:
        return list(self._elements)

    def index(self, elem: Any) -> int:
        return self._index[elem]
