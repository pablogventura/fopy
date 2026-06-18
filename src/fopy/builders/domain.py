"""Named universe elements."""

from __future__ import annotations

from collections.abc import Hashable, Iterator
from typing import Any


class Domain:
    """Ordered collection of structure elements with optional attribute access."""

    def __init__(self, *elements: Hashable) -> None:
        """Create a domain from ordered *elements*.

        Args:
            *elements: Universe elements in display order.
        """
        self._elements = list(elements)
        self._index = {e: i for i, e in enumerate(self._elements)}

    def __iter__(self) -> Iterator[Any]:
        """Iterate over domain elements in order."""
        return iter(self._elements)

    def __len__(self) -> int:
        """Return the number of domain elements."""
        return len(self._elements)

    def __getitem__(self, idx: int | str) -> Any:
        """Access an element by index or attribute name.

        Args:
            idx: Integer index or element name.

        Returns:
            The element at *idx*, or its name when accessed by string label.
        """
        if isinstance(idx, int):
            return self._elements[idx]
        return getattr(self, idx)

    def __getattr__(self, name: str) -> Any:
        """Return the string label of a named domain element.

        Args:
            name: Element name registered in the domain.

        Returns:
            *name* when it labels a domain element.

        Raises:
            AttributeError: If *name* is not a domain element.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        if name in self._index:
            return name
        raise AttributeError(name)

    def list(self) -> list[Any]:
        """Return a copy of the ordered domain elements."""
        return list(self._elements)

    def index(self, elem: Any) -> int:
        """Return the index of *elem* in the domain.

        Args:
            elem: Domain element to look up.

        Returns:
            Zero-based index of *elem*.
        """
        return self._index[elem]
