"""Draw Hasse diagrams for congruence and subalgebra lattices."""

from __future__ import annotations

from collections.abc import Hashable, Sequence

from fopy.finite.models import Model
from fopy.universal import Congruence, congruence_lattice, subalgebra_lattice


def draw_congruence_lattice(model: Model, *, filename: str | None = None) -> object:
    """Layout and render the congruence lattice of *model*.

    Requires the optional ``draw`` extra (matplotlib).

    Args:
        model: Finite algebra whose congruence lattice is drawn.
        filename: When set, write SVG or PNG to this path.

    Returns:
        Matplotlib figure object from :func:`~fopy.draw.draw_lattice`.

    Raises:
        ValueError: If the congruence lattice is empty.
        ImportError: If matplotlib is not installed.
    """

    from fopy.draw import draw_lattice

    congruences = list(congruence_lattice(model))
    if not congruences:
        raise ValueError("empty congruence lattice")
    elements: list[Hashable] = list(range(len(congruences)))
    labels: dict[Hashable, str] = {i: _congruence_label(c) for i, c in enumerate(congruences)}
    covers = _congruence_covers(congruences)
    return draw_lattice(elements, covers=covers, filename=filename, labels=labels)


def draw_subalgebra_lattice(model: Model, *, filename: str | None = None) -> object:
    """Layout and render the subalgebra lattice of *model*.

    Requires the optional ``draw`` extra (matplotlib).

    Args:
        model: Finite algebra whose subuniverses are drawn.
        filename: When set, write SVG or PNG to this path.

    Returns:
        Matplotlib figure object from :func:`~fopy.draw.draw_lattice`.

    Raises:
        ValueError: If the subalgebra lattice is empty.
        ImportError: If matplotlib is not installed.
    """

    from fopy.draw import draw_lattice

    subs = list(subalgebra_lattice(model))
    if not subs:
        raise ValueError("empty subalgebra lattice")
    elements: list[Hashable] = list(range(len(subs)))
    labels: dict[Hashable, str] = {i: _subalgebra_label(s) for i, s in enumerate(subs)}
    covers = _subalgebra_covers(subs)
    return draw_lattice(elements, covers=covers, filename=filename, labels=labels)


def _subalgebra_label(sub: set[int]) -> str:
    return "{" + ",".join(str(x) for x in sorted(sub)) + "}"


def _subalgebra_covers(subs: Sequence[set[int]]) -> list[tuple[int, int]]:
    covers: list[tuple[int, int]] = []
    indexed = list(enumerate(subs))
    for i, a in indexed:
        for j, b in indexed:
            if a == b or not a < b:
                continue
            minimal = True
            for _k, c in indexed:
                if c in (a, b):
                    continue
                if a < c < b:
                    minimal = False
                    break
            if minimal:
                covers.append((i, j))
    return covers


def _congruence_label(c: Congruence) -> str:
    parts = ["".join(str(x) for x in sorted(block)) for block in c.classes]
    return "/".join(parts)


def _congruence_covers(congruences: Sequence[Congruence]) -> list[tuple[int, int]]:
    covers: list[tuple[int, int]] = []
    index = {c.classes: i for i, c in enumerate(congruences)}

    def refines(a: Congruence, b: Congruence) -> bool:
        """Return whether every block of *a* is contained in some block of *b*."""

        for block in a.classes:
            for x in block:
                for y in block:
                    if y == x:
                        continue
                    found = False
                    for bblock in b.classes:
                        if x in bblock and y in bblock:
                            found = True
                            break
                    if not found:
                        return False
        return True

    for a in congruences:
        for b in congruences:
            if a.classes == b.classes:
                continue
            if refines(a, b) and not refines(b, a):
                minimal = True
                for c in congruences:
                    if c.classes == a.classes or c.classes == b.classes:
                        continue
                    if refines(a, c) and refines(c, b) and not refines(c, a):
                        minimal = False
                        break
                if minimal:
                    covers.append((index[a.classes], index[b.classes]))
    return covers
