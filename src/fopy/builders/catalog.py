"""Standard example structures."""

from __future__ import annotations

from fopy.builders.from_poset import from_covers, from_upper_covers
from fopy.signature import Signature
from fopy.structures import Structure


def chain(n: int, relation: str = "leq") -> Structure:
    """Build a linear chain poset on ``{0, …, n - 1}``.

    Args:
        n: Number of elements in the chain.
        relation: Name of the order relation symbol.

    Returns:
        Structure whose order is the chain cover relation.
    """
    sig = Signature(relations={relation: 2})
    covers = [(i, i + 1) for i in range(n - 1)]
    return from_covers(list(range(n)), covers, relation=relation, signature=sig)


def boolean_lattice(n: int, meet: str = "meet", join: str = "join", leq: str = "leq") -> Structure:
    """Build the power-set Boolean lattice ``B_n`` on ``{0, …, n - 1}``.

    Elements are bitmasks ``0 … 2^n - 1`` with meet/join as bitwise
    ``&`` / ``|`` and ``leq`` as subset order.

    Args:
        n: Number of atoms (dimension of the lattice).
        meet: Symbol for the meet operation.
        join: Symbol for the join operation.
        leq: Symbol for the partial-order relation.

    Returns:
        Boolean lattice structure on ``2^n`` elements.
    """
    size = 2**n
    universe = list(range(size))

    def meet_op(a: int, b: int) -> int:
        """Bitwise meet (``a & b``) on lattice element encodings."""

        return a & b

    def join_op(a: int, b: int) -> int:
        """Bitwise join (``a | b``) on lattice element encodings."""

        return a | b

    def leq_op(a: int, b: int) -> bool:
        """Subset order: ``a`` is below ``b`` iff ``a & b == a``."""

        return (a & b) == a

    sig = Signature(functions={meet: 2, join: 2}, relations={leq: 2})

    meet_tbl = {(a, b): meet_op(a, b) for a in universe for b in universe}
    join_tbl = {(a, b): join_op(a, b) for a in universe for b in universe}
    leq_rel = {(a, b) for a in universe for b in universe if leq_op(a, b)}
    return Structure.from_tables(
        sig,
        universe,
        functions={meet: meet_tbl, join: join_tbl},
        relations={leq: leq_rel},
    )


def m3(relation: str = "leq") -> Structure:
    """Build the diamond lattice ``M3`` (four elements).

    Args:
        relation: Name of the order relation symbol.

    Returns:
        ``M3`` poset as a :class:`~fopy.structures.Structure`.
    """
    return from_upper_covers([[1, 2], [], [3], [3]], names=["0", "1", "2", "3"], relation=relation)


def n5(relation: str = "leq") -> Structure:
    """Build the pentagon lattice ``N5``.

    Args:
        relation: Name of the order relation symbol.

    Returns:
        ``N5`` poset as a :class:`~fopy.structures.Structure`.
    """
    return from_upper_covers(
        [[1], [2], [3], [], [4]],
        names=["0", "1", "2", "3", "4"],
        relation=relation,
    )


def retrombo(relation: str = "leq") -> Structure:
    """Build the retrombo (diamond) poset on four elements.

    Args:
        relation: Name of the order relation symbol.

    Returns:
        Four-element diamond poset as a :class:`~fopy.structures.Structure`.
    """
    return from_upper_covers([[1, 2], [], [3], [3]], names=["0", "1", "2", "3"], relation=relation)


def b3(relation: str = "leq") -> Structure:
    """Build the Boolean lattice ``B3`` (eight elements).

    Args:
        relation: Name of the partial-order relation symbol.

    Returns:
        Three-dimensional Boolean lattice structure.
    """
    return boolean_lattice(3, leq=relation)


def semilattice(n: int, meet: str = "meet") -> Structure:
    """Build an ``n``-element chain semilattice with meet as minimum.

    The universe is ``{0, …, n - 1}`` ordered linearly; the binary
    operation *meet* returns the smaller element. This is the unique
    ``n``-element meet-semilattice up to isomorphism (a chain).

    Args:
        n: Number of semilattice elements (must be at least 1).
        meet: Symbol for the meet operation.

    Returns:
        Structure with one binary function *meet*.

    Raises:
        ValueError: If ``n < 1``.
    """
    if n < 1:
        raise ValueError("semilattice requires n >= 1")
    universe = list(range(n))
    sig = Signature(functions={meet: 2})
    meet_tbl = {(a, b): min(a, b) for a in universe for b in universe}
    return Structure.from_tables(sig, universe, functions={meet: meet_tbl})


def group_cyclic(n: int, op: str = "add") -> Structure:
    """Build the cyclic group ``Z_n`` (additive notation).

    Universe elements are ``0, …, n - 1`` with *op* interpreted as
    addition modulo ``n``. For ``n = 1`` the group is trivial.

    Args:
        n: Group order (must be at least 1).
        op: Symbol for the group operation.

    Returns:
        Structure with one binary function *op*.

    Raises:
        ValueError: If ``n < 1``.
    """
    if n < 1:
        raise ValueError("group_cyclic requires n >= 1")
    universe = list(range(n))
    sig = Signature(functions={op: 2})
    tbl = {(a, b): (a + b) % n for a in universe for b in universe}
    return Structure.from_tables(sig, universe, functions={op: tbl})


def monoid_free(n: int, op: str = "mul", unit: str = "e") -> Structure:
    """Build the free monoid on one generator, truncated to size ``n``.

    Elements are ``0, …, n - 1`` where ``0`` is the identity and
    ``i * j = i + j`` when ``i + j < n``, otherwise the product is
    undefined in the table (mapped to ``0`` as a sentinel for overflow).
    Intended for small ``n`` in examples and tests.

    Args:
        n: Monoid size (at least 2 for a nontrivial generator).
        op: Binary monoid operation symbol.
        unit: Nullary constant for the identity (value ``0``).

    Returns:
        Structure with constant *unit* and binary *op*.

    Raises:
        ValueError: If ``n < 1``.
    """
    if n < 1:
        raise ValueError("monoid_free requires n >= 1")
    universe = list(range(n))
    sig = Signature(functions={op: 2, unit: 0})
    tbl: dict[tuple[int, int], int] = {}
    for a in universe:
        for b in universe:
            if a == 0:
                tbl[(a, b)] = b
            elif b == 0:
                tbl[(a, b)] = a
            elif a + b < n:
                tbl[(a, b)] = a + b
            else:
                tbl[(a, b)] = 0
    return Structure.from_tables(sig, universe, functions={op: tbl, unit: 0})


def ring_zn(n: int, add: str = "add", mul: str = "mul") -> Structure:
    """Build the ring ``Z/nZ`` of integers modulo ``n``.

    Args:
        n: Modulus (must be at least 1).
        add: Symbol for addition modulo ``n``.
        mul: Symbol for multiplication modulo ``n``.

    Returns:
        Structure with binary *add* and *mul*.

    Raises:
        ValueError: If ``n < 1``.
    """
    if n < 1:
        raise ValueError("ring_zn requires n >= 1")
    universe = list(range(n))
    sig = Signature(functions={add: 2, mul: 2})
    add_tbl = {(a, b): (a + b) % n for a in universe for b in universe}
    mul_tbl = {(a, b): (a * b) % n for a in universe for b in universe}
    return Structure.from_tables(
        sig,
        universe,
        functions={add: add_tbl, mul: mul_tbl},
    )


def heyting_chain(n: int, meet: str = "meet", join: str = "join", imp: str = "imp") -> Structure:
    """Build the ``n``-element Heyting algebra (linear chain).

    On ``{0, …, n - 1}`` with bottom ``0`` and top ``n - 1``:
    meet is ``min``, join is ``max``, and implication satisfies
    ``a → b = n - 1`` when ``a ≤ b``, else ``b``.

    Args:
        n: Chain length (at least 1).
        meet: Meet operation symbol.
        join: Join operation symbol.
        imp: Implication operation symbol.

    Returns:
        Heyting chain as a :class:`~fopy.structures.Structure`.

    Raises:
        ValueError: If ``n < 1``.
    """
    if n < 1:
        raise ValueError("heyting_chain requires n >= 1")
    universe = list(range(n))
    top = n - 1
    sig = Signature(functions={meet: 2, join: 2, imp: 2})
    meet_tbl = {(a, b): min(a, b) for a in universe for b in universe}
    join_tbl = {(a, b): max(a, b) for a in universe for b in universe}
    imp_tbl = {(a, b): (top if a <= b else b) for a in universe for b in universe}
    return Structure.from_tables(
        sig,
        universe,
        functions={meet: meet_tbl, join: join_tbl, imp: imp_tbl},
    )
