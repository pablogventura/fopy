"""FO and primitive-positive type signatures for tuples on finite models."""

from __future__ import annotations

from typing import Any

from fopy.finite.models import Model

DEFAULT_PP_DEPTH = 2


def atomic_pp_type(
    model: Model,
    tuple_vals: tuple[int, ...] | list[int],
    *,
    max_depth: int = DEFAULT_PP_DEPTH,
) -> tuple[Any, ...]:
    """Compute the primitive-positive (quantifier-free) type of a tuple.

    Delegates to the same term-evaluation signature used by
    :func:`~fopy.finite.explain.atomic_type`: two tuples share a label when no
    quantifier-free formula over the model signature can distinguish them at the
    given term depth.

    Args:
        model: Finite model providing operation tables.
        tuple_vals: Universe indices forming the tuple to classify.
        max_depth: Maximum term nesting depth when evaluating signatures.

    Returns:
        Hashable signature tuple used to compare atomic PP types.
    """
    from fopy.finite.explain import atomic_type

    return atomic_type(model, tuple_vals, max_depth=max_depth)


def fo_type(
    model: Model,
    tuple_vals: tuple[int, ...] | list[int],
    k: int,
    arity_vars: int,
) -> tuple[Any, ...]:
    """Refine a tuple type by bounded first-order information up to rank *k*.

    For ``k <= 0`` this coincides with :func:`atomic_pp_type`.  For ``k > 0`` the
    label extends the ``(k-1)``-type with the sorted multiset of ``(k-1)``-types
    of *neighbour* tuples that differ in exactly one coordinate (Gaifman-style
    refinement on a finite universe).

    Args:
        model: Finite structure used for term evaluation and neighbour moves.
        tuple_vals: Tuple of universe elements to classify.
        k: Quantifier-rank / refinement depth (non-negative).
        arity_vars: Arity of the relation variables (used for PP term depth).

    Returns:
        Hashable refined type label suitable for partition refinement.
    """
    row = tuple(tuple_vals)
    if k <= 0:
        return atomic_pp_type(model, row, max_depth=max(arity_vars, DEFAULT_PP_DEPTH))

    prev = fo_type(model, row, k - 1, arity_vars)
    universe = model.universe
    neighbour_types: list[tuple[Any, ...]] = []
    for i in range(len(row)):
        for u in universe:
            if row[i] == u:
                continue
            neighbour = row[:i] + (u,) + row[i + 1 :]
            neighbour_types.append(fo_type(model, neighbour, k - 1, arity_vars))
    return (prev, tuple(sorted(neighbour_types)))


def max_universe_for_ktypes(arity: int, *, limit: int = 256) -> int:
    """Return the largest universe size allowed for *arity*-tuples under *limit*.

    Tuple partitions used by the fragment checkers enumerate ``|U|^arity``
    assignments; this helper picks the maximum ``|U|`` that keeps that product at
    or below *limit* (default 256).

    Args:
        arity: Relation arity (positive integer).
        limit: Maximum number of tuples to enumerate.

    Returns:
        Largest integer ``m >= 1`` with ``m ** arity <= limit``.

    Raises:
        ValueError: If *arity* is not positive.
    """
    if arity <= 0:
        raise ValueError("arity must be positive")
    size = 1
    while (size + 1) ** arity <= limit:
        size += 1
    return size
