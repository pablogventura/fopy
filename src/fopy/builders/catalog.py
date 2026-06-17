"""Standard example structures."""

from __future__ import annotations

from fopy.builders.from_poset import from_covers, from_upper_covers
from fopy.signature import Signature


def chain(n: int, relation: str = "leq"):
    sig = Signature(relations={relation: 2})
    covers = [(i, i + 1) for i in range(n - 1)]
    return from_covers(list(range(n)), covers, relation=relation, signature=sig)


def boolean_lattice(n: int, meet: str = "meet", join: str = "join", leq: str = "leq"):
    """Power set lattice B_n on {0,...,n-1} as bitmasks 0..2^n-1."""
    size = 2**n
    universe = list(range(size))

    def meet_op(a: int, b: int) -> int:
        return a & b

    def join_op(a: int, b: int) -> int:
        return a | b

    def leq_op(a: int, b: int) -> bool:
        return (a & b) == a

    sig = Signature(functions={meet: 2, join: 2}, relations={leq: 2})
    from fopy.structures import Structure

    meet_tbl = {(a, b): meet_op(a, b) for a in universe for b in universe}
    join_tbl = {(a, b): join_op(a, b) for a in universe for b in universe}
    leq_rel = {(a, b) for a in universe for b in universe if leq_op(a, b)}
    return Structure.from_tables(sig, universe, functions={meet: meet_tbl, join: join_tbl}, relations={leq: leq_rel})


def m3(relation: str = "leq"):
    """Diamond M3 (4 elements)."""
    return from_upper_covers([[1, 2], [], [3], [3]], names=["0", "1", "2", "3"], relation=relation)


def n5(relation: str = "leq"):
    """Pentagon N5."""
    return from_upper_covers([[1], [2], [3], [], [4]], names=["0", "1", "2", "3", "4"], relation=relation)


def retrombo(relation: str = "leq"):
    """Diamond poset (retrombo) on four elements."""
    return from_upper_covers([[1, 2], [], [3], [3]], names=["0", "1", "2", "3"], relation=relation)


def b3(relation: str = "leq"):
    """Boolean lattice B3 (8 elements)."""
    return boolean_lattice(3, leq=relation)
