"""Partition refinement utilities for tuple typing on finite models."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from itertools import product

from fopy.finite.models import Model
from fopy.finite.relops import Relation

MAX_TUPLE_PARTITION = 256


class TuplePartition:
    """Partition of arity-fixed tuples refined by hashable type keys.

    Blocks start as a single class containing every tuple over
    :attr:`~fopy.finite.models.Model.universe`.  Call :meth:`refine` with a key
    function (for example :func:`~fopy.finite.ktypes.atomic_pp_type`) to split
    blocks into finer equivalence classes.

    Attributes:
        blocks: Current list of frozenset blocks covering all tuples.
    """

    def __init__(self, tuples: list[tuple[int, ...]]) -> None:
        """Initialize a partition with one block containing all *tuples*."""
        self.blocks: list[frozenset[tuple[int, ...]]] = [frozenset(tuples)]

    @classmethod
    def from_model(cls, model: Model, arity: int) -> TuplePartition:
        """Build the full tuple partition for *model* at relation arity *arity*.

        Args:
            model: Finite model supplying the universe.
            arity: Number of coordinates per tuple.

        Returns:
            Fresh partition with one block per enumerated tuple.

        Raises:
            ValueError: If ``|U|^arity`` exceeds :data:`MAX_TUPLE_PARTITION`.
        """
        tuples = enumerate_tuples(model, arity)
        return cls(tuples)

    def refine(self, key_fn: Callable[[tuple[int, ...]], Hashable]) -> None:
        """Split each block by the hashable key returned by *key_fn*.

        Args:
            key_fn: Maps a tuple to its current type label; tuples with equal
                keys remain in the same refined block.
        """
        refined: list[frozenset[tuple[int, ...]]] = []
        for block in self.blocks:
            buckets: dict[Hashable, list[tuple[int, ...]]] = {}
            for row in block:
                buckets.setdefault(key_fn(row), []).append(row)
            refined.extend(frozenset(bucket) for bucket in buckets.values())
        self.blocks = refined

    def is_target_pure(self, target: Relation) -> bool:
        """Return whether *target* is constant on every block.

        A block is *target-pure* when all its tuples agree on membership in
        *target*; the relation is partition-definable exactly when every block is
        pure.

        Args:
            target: Relation whose extension is compared on each block.

        Returns:
            ``True`` when no block mixes tuples inside and outside *target*.
        """
        for block in self.blocks:
            flags = {target.contains(row) for row in block}
            if len(flags) > 1:
                return False
        return True

    def witness_pair(self, target: Relation) -> tuple[tuple[int, ...], tuple[int, ...]] | None:
        """Return an in/out pair from a mixed block, if one exists.

        Args:
            target: Relation used to separate tuples inside a block.

        Returns:
            ``(t_in, t_out)`` with ``t_in`` in the target and ``t_out`` not in
            the target, or ``None`` when every block is target-pure.
        """
        for block in self.blocks:
            inside = [row for row in block if target.contains(row)]
            outside = [row for row in block if not target.contains(row)]
            if inside and outside:
                return inside[0], outside[0]
        return None


def enumerate_tuples(model: Model, arity: int) -> list[tuple[int, ...]]:
    """List every arity-tuple over ``model.universe`` with a size guard.

    Args:
        model: Finite model supplying the universe.
        arity: Tuple length.

    Returns:
        All tuples in lexicographic product order.

    Raises:
        ValueError: If ``|U|^arity`` exceeds :data:`MAX_TUPLE_PARTITION`.
    """
    universe = model.universe
    count = len(universe) ** arity
    if count > MAX_TUPLE_PARTITION:
        msg = (
            f"Cannot enumerate {arity}-tuples: |U|^{arity} = {count} "
            f"exceeds MAX_TUPLE_PARTITION={MAX_TUPLE_PARTITION}."
        )
        raise ValueError(msg)
    return list(product(universe, repeat=arity))


def enumerate_tuples_unbounded(model: Model, arity: int) -> list[tuple[int, ...]]:
    """List every arity-tuple over ``model.universe`` without a size guard.

    Used as a fallback when :func:`enumerate_tuples` refuses large products
    (for example inside HIT on big universes).
    """
    return list(product(model.universe, repeat=arity))
