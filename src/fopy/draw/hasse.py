"""Hasse diagram cover edges."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Sequence

from fopy.draw.poset import index_elements, validate_poset


def hasse_covers(
    elements: Sequence[Hashable],
    leq: Callable[[Hashable, Hashable], bool] | None = None,
    covers: Iterable[tuple[Hashable, Hashable]] | None = None,
) -> set[tuple[Hashable, Hashable]]:
    """
    Return Hasse cover edges.

    If covers are given and leq is None, return them unchanged.
    Otherwise derive covers from the order relation.
    """
    ordered, _ = index_elements(elements)
    if covers is not None and leq is None:
        return set(covers)

    matrix = validate_poset(ordered, leq=leq, covers=covers)
    n = len(ordered)
    result: set[tuple[Hashable, Hashable]] = set()
    for i in range(n):
        for j in range(n):
            if i == j or not matrix[i][j]:
                continue
            if any(k != i and k != j and matrix[i][k] and matrix[k][j] for k in range(n)):
                continue
            result.add((ordered[i], ordered[j]))
    return result


def cover_adjacency(
    elements: Sequence[Hashable],
    covers: set[tuple[Hashable, Hashable]],
) -> tuple[list[list[int]], list[list[int]]]:
    """Return lower and upper cover adjacency lists by index."""
    ordered, index = index_elements(elements)
    n = len(ordered)
    lowers: list[list[int]] = [[] for _ in range(n)]
    uppers: list[list[int]] = [[] for _ in range(n)]
    for a, b in covers:
        i, j = index[a], index[b]
        lowers[j].append(i)
        uppers[i].append(j)
    return lowers, uppers
