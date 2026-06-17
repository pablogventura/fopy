"""Build structures from order relations and Hasse covers."""

from __future__ import annotations

from typing import Any, Callable, Iterable

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
    """Sage-style: upper_covers[i] lists indices j with i < j (covering)."""
    n = len(upper_covers)
    elements = names if names is not None else list(range(n))
    covers: list[tuple[Any, Any]] = []
    for i, ups in enumerate(upper_covers):
        for j in ups:
            covers.append((elements[i], elements[j]))
    return from_covers(list(elements), covers, relation=relation)
