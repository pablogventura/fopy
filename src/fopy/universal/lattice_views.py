"""List-like lattice views with optional drawing for notebooks."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fopy.finite.models import Model
    from fopy.universal import Congruence


@dataclass
class CongruenceLattice:
    """All congruences on a finite algebra, with a :meth:`draw` helper.

    Behaves like a read-only sequence of :class:`~fopy.universal.Congruence`
    blocks while exposing notebook-friendly rendering.
    """

    model: Model
    _items: list[Congruence]

    def draw(self, *, filename: str | None = None) -> object:
        """Draw the Hasse diagram of this congruence lattice (requires ``[draw]``)."""
        from fopy.universal.draw import draw_congruence_lattice

        return draw_congruence_lattice(self.model, filename=filename)

    def __iter__(self) -> Iterator[Congruence]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> Congruence:
        return self._items[index]

    def __repr__(self) -> str:
        return f"CongruenceLattice(model, {len(self._items)} congruences)"


@dataclass
class SubalgebraLattice:
    """All subuniverses of a finite algebra, with a :meth:`draw` helper."""

    model: Model
    _items: list[set[int]]

    def draw(self, *, filename: str | None = None) -> object:
        """Draw the Hasse diagram of this subalgebra lattice (requires ``[draw]``)."""
        from fopy.universal.draw import draw_subalgebra_lattice

        return draw_subalgebra_lattice(self.model, filename=filename)

    def __iter__(self) -> Iterator[set[int]]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> set[int]:
        return self._items[index]

    def __repr__(self) -> str:
        return f"SubalgebraLattice(model, {len(self._items)} subalgebras)"
