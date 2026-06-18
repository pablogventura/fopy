"""Finite poset validation and order-relation utilities."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Sequence
from typing import TypeVar

T = TypeVar("T", bound=Hashable)


def index_elements(elements: Sequence[T]) -> tuple[list[T], dict[T, int]]:
    """Return a copy of elements and a stable element-to-index map."""
    ordered = list(elements)
    index = {element: i for i, element in enumerate(ordered)}
    if len(index) != len(ordered):
        raise ValueError("elements must be unique")
    return ordered, index


def leq_matrix(elements: Sequence[T], leq: Callable[[T, T], bool]) -> list[list[bool]]:
    """Build a reflexive-transitive closure matrix from a leq predicate."""
    n = len(elements)
    matrix = [[False] * n for _ in range(n)]
    for i, a in enumerate(elements):
        for j, b in enumerate(elements):
            if leq(a, b):
                matrix[i][j] = True
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if not matrix[i][j]:
                    continue
                for k in range(n):
                    if matrix[j][k] and not matrix[i][k]:
                        matrix[i][k] = True
                        changed = True
    return matrix


def leq_from_matrix(elements: Sequence[T], matrix: list[list[bool]]) -> Callable[[T, T], bool]:
    """Wrap a boolean matrix as a leq predicate."""
    index = {element: i for i, element in enumerate(elements)}
    return lambda a, b: matrix[index[a]][index[b]]


def leq_closure(
    elements: Sequence[T],
    pairs: Iterable[tuple[T, T]],
) -> set[tuple[T, T]]:
    """Reflexive-transitive closure of explicit order pairs."""
    ordered, index = index_elements(elements)
    n = len(ordered)
    matrix = [[False] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = True
    for a, b in pairs:
        if a not in index or b not in index:
            raise ValueError(f"pair ({a!r}, {b!r}) uses unknown element")
        matrix[index[a]][index[b]] = True
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if not matrix[i][j]:
                    continue
                for k in range(n):
                    if matrix[j][k] and not matrix[i][k]:
                        matrix[i][k] = True
                        changed = True
    return {(ordered[i], ordered[j]) for i in range(n) for j in range(n) if matrix[i][j]}


def validate_poset(
    elements: Sequence[T],
    leq: Callable[[T, T], bool] | None = None,
    covers: Iterable[tuple[T, T]] | None = None,
) -> list[list[bool]]:
    """
    Validate that leq or covers define a partial order.

    Returns the reflexive-transitive closure matrix.
    """
    ordered, index = index_elements(elements)
    n = len(ordered)
    if leq is not None:
        matrix = leq_matrix(ordered, leq)
    elif covers is not None:
        pairs = set(covers)
        matrix = [[False] * n for _ in range(n)]
        for i in range(n):
            matrix[i][i] = True
        for a, b in pairs:
            if a not in index or b not in index:
                raise ValueError(f"cover ({a!r}, {b!r}) uses unknown element")
            matrix[index[a]][index[b]] = True
        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(n):
                    if not matrix[i][j]:
                        continue
                    for k in range(n):
                        if matrix[j][k] and not matrix[i][k]:
                            matrix[i][k] = True
                            changed = True
    else:
        raise ValueError("provide leq or covers")

    for i in range(n):
        for j in range(n):
            if i != j and matrix[i][j] and matrix[j][i]:
                raise ValueError(f"antisymmetry violated: {ordered[i]!r} and {ordered[j]!r}")

    return matrix


def comparable(matrix: list[list[bool]], i: int, j: int) -> bool:
    """True when i <= j or j <= i."""
    return matrix[i][j] or matrix[j][i]


def minimal_indices(matrix: list[list[bool]]) -> list[int]:
    """Indices of minimal elements."""
    n = len(matrix)
    return [i for i in range(n) if not any(matrix[j][i] for j in range(n) if j != i)]


def maximal_indices(matrix: list[list[bool]]) -> list[int]:
    """Indices of maximal elements."""
    n = len(matrix)
    return [i for i in range(n) if not any(matrix[i][j] for j in range(n) if j != i)]
