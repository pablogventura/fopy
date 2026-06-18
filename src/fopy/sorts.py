"""Sort symbols for many-sorted first-order logic (lite)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Sort:
    """Named sort in a many-sorted signature."""

    name: str

    def __repr__(self) -> str:
        return self.name


DEFAULT_SORT = Sort("U")
