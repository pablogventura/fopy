"""Public API for Hasse diagram layout and drawing."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from fopy.draw.examples import boolean_lattice, chain, m3, n5
from fopy.draw.forces import simulate_forces
from fopy.draw.hasse import hasse_covers
from fopy.draw.layout3d import initial_positions_3d
from fopy.draw.poset import index_elements, validate_poset
from fopy.draw.project import find_best_view
from fopy.draw.ranking import compute_levels, normalize_levels
from fopy.draw.render import render_lattice

__all__ = [
    "LatticeLayout",
    "boolean_lattice",
    "chain",
    "draw_lattice",
    "draw_structure",
    "layout_lattice",
    "m3",
    "n5",
]


@dataclass
class LatticeLayout:
    """Computed layout for a finite poset or lattice."""

    elements: list[Hashable]
    covers: set[tuple[Hashable, Hashable]]
    positions_3d: np.ndarray
    positions_2d: np.ndarray
    azimuth: float
    elevation: float
    levels: np.ndarray


def layout_lattice(
    elements: Sequence[Hashable],
    leq: Callable[[Hashable, Hashable], bool] | None = None,
    covers: Iterable[tuple[Hashable, Hashable]] | None = None,
    *,
    seed: int = 42,
) -> LatticeLayout:
    """
    Compute a Freese/LatDraw-inspired 3D layout and best 2D projection.

    Provide either a partial-order predicate ``leq`` or Hasse ``covers``.
    """
    ordered, index = index_elements(elements)
    matrix = validate_poset(ordered, leq=leq, covers=covers)
    cover_set = hasse_covers(ordered, leq=leq, covers=covers)
    cover_edges = [(index[a], index[b]) for a, b in cover_set]

    rank = compute_levels(matrix)
    levels = normalize_levels(rank.levels)

    positions_3d = initial_positions_3d(levels, seed=seed)
    positions_3d = simulate_forces(
        positions_3d,
        levels,
        matrix,
        cover_edges,
        seed=seed,
    )

    azimuth, elevation, positions_2d = find_best_view(positions_3d, cover_edges)

    return LatticeLayout(
        elements=ordered,
        covers=cover_set,
        positions_3d=positions_3d,
        positions_2d=positions_2d,
        azimuth=azimuth,
        elevation=elevation,
        levels=levels,
    )


def draw_structure(
    structure: Any,
    relation: str = "leq",
    *,
    seed: int = 42,
    filename: str | Path | None = None,
    labels: dict[Hashable, str] | None = None,
):
    """Draw Hasse diagram from a :class:`fopy.structures.Structure`."""
    from fopy.structures import Structure

    if not isinstance(structure, Structure):
        raise TypeError("structure must be a fopy.structures.Structure")
    if relation not in structure.signature.relations:
        raise KeyError(f"Relation {relation!r} not in structure signature")
    universe = list(structure.universe)
    rel_data = structure.relations[relation]
    if isinstance(rel_data, set):
        leq_set = rel_data

        def leq(a: Hashable, b: Hashable) -> bool:
            return (a, b) in leq_set
    else:

        def leq(a: Hashable, b: Hashable) -> bool:
            return bool(structure.call_relation(relation, (a, b)))

    return draw_lattice(universe, leq=leq, seed=seed, filename=filename, labels=labels)


def draw_lattice(
    elements: Sequence[Hashable] | tuple[Sequence[Hashable], Any],
    leq: Callable[[Hashable, Hashable], bool] | None = None,
    covers: Iterable[tuple[Hashable, Hashable]] | None = None,
    *,
    seed: int = 42,
    filename: str | Path | None = None,
    labels: dict[Hashable, str] | None = None,
):
    """
    Layout and render a Hasse diagram.

    ``elements`` may be a sequence or a pair ``(elements, leq)`` or
    ``(elements, covers)`` as returned by the example helpers.
    """
    if isinstance(elements, tuple) and len(elements) == 2:
        elems, rel = elements
        if callable(rel):
            leq = rel
        else:
            covers = rel
        elements = elems

    layout = layout_lattice(elements, leq=leq, covers=covers, seed=seed)
    return render_lattice(
        layout.elements,
        layout.positions_2d,
        layout.covers,
        filename=filename,
        labels=labels,
    )
