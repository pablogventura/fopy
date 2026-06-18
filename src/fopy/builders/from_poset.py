"""Build structures from order relations and Hasse covers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from fopy.signature import Signature
from fopy.structures import Structure


def _reflexive_transitive_closure(
    elements: list[Any], leq: Callable[[Any, Any], bool]
) -> set[tuple[Any, Any]]:
    rel = {(a, a) for a in elements}
    for a in elements:
        for b in elements:
            if leq(a, b):
                rel.add((a, b))
    changed = True
    while changed:
        changed = False
        for a in elements:
            for b in elements:
                if (a, b) in rel:
                    for c in elements:
                        if (b, c) in rel and (a, c) not in rel:
                            rel.add((a, c))
                            changed = True
    return rel


def hasse_covers(
    elements: list[Any],
    leq: Callable[[Any, Any], bool] | None = None,
    covers: Iterable[tuple[Any, Any]] | None = None,
) -> set[tuple[Any, Any]]:
    """Compute Hasse cover edges of a partial order.

    Args:
        elements: Universe elements.
        leq: Optional predicate for ``a ≤ b``; required when *covers* is omitted.
        covers: Optional explicit cover edges; when given without *leq*, returned as-is.

    Returns:
        Set of cover pairs ``(a, b)`` with ``a < b`` and no intermediate element.

    Raises:
        ValueError: If neither *leq* nor *covers* is provided.
    """
    if covers is not None:
        cover_set = set(covers)
        if leq is None:
            return cover_set
    else:
        if leq is None:
            raise ValueError("Provide leq or covers")
        cover_set = set()
        rel = _reflexive_transitive_closure(elements, leq)
        for a in elements:
            for b in elements:
                if a == b or (a, b) not in rel:
                    continue
                if not any((a, c) in rel and (c, b) in rel and a != c and c != b for c in elements):
                    cover_set.add((a, b))
    return cover_set


def from_leq(
    elements: list[Any],
    leq: Callable[[Any, Any], bool],
    relation: str = "leq",
    signature: Signature | None = None,
) -> Structure:
    """Build a structure from a partial-order predicate.

    Args:
        elements: Universe elements.
        leq: Predicate returning ``True`` when the first argument is below the second.
        relation: Name of the order relation symbol.
        signature: Optional signature; defaults to a single binary relation *relation*.

    Returns:
        Structure whose *relation* is the reflexive-transitive closure of *leq*.
    """
    sig = signature or Signature(relations={relation: 2})
    rel = _reflexive_transitive_closure(elements, leq)
    return Structure.from_tables(sig, elements, relations={relation: rel})


def from_covers(
    universe: list[Any],
    covers: Iterable[tuple[Any, Any]],
    relation: str = "leq",
    signature: Signature | None = None,
    infer_leq: bool = True,
) -> Structure:
    """Build a structure from Hasse cover edges.

    Args:
        universe: Universe elements.
        covers: Cover edges ``(a, b)`` with ``a < b`` and no element strictly between.
        relation: Name of the order relation symbol.
        signature: Optional signature; defaults to a single binary relation *relation*.
        infer_leq: If ``True``, compute the reflexive-transitive closure of *covers*;
            otherwise store *covers* directly as the relation.

    Returns:
        Poset structure on *universe*.
    """
    cover_list = list(covers)
    elements = list(universe)
    if infer_leq:
        leq_pairs: set[tuple[Any, Any]] = set(cover_list)
        for a in elements:
            leq_pairs.add((a, a))
        changed = True
        while changed:
            changed = False
            for x, y in list(leq_pairs):
                for z, w in list(leq_pairs):
                    if y == z and (x, w) not in leq_pairs:
                        leq_pairs.add((x, w))
                        changed = True
        return from_leq(elements, lambda a, b: (a, b) in leq_pairs, relation, signature)
    sig = signature or Signature(relations={relation: 2})
    return Structure.from_tables(sig, elements, relations={relation: set(cover_list)})


def from_upper_covers(
    upper_covers: list[list[int]],
    names: list[str] | None = None,
    relation: str = "leq",
) -> Structure:
    """Build a poset from Sage-style upper-cover lists.

    ``upper_covers[i]`` lists indices ``j`` such that ``i < j`` is a cover relation.

    Args:
        upper_covers: For each element index, list of indices of upper covers.
        names: Optional element labels; defaults to ``0, …, n - 1``.
        relation: Name of the order relation symbol.

    Returns:
        Poset structure inferred from the cover lists.
    """
    n = len(upper_covers)
    elements: list[str | int] = list(names) if names is not None else list(range(n))
    covers: list[tuple[Any, Any]] = []
    for i, ups in enumerate(upper_covers):
        for j in ups:
            covers.append((elements[i], elements[j]))
    return from_covers(list(elements), covers, relation=relation)
