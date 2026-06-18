"""Bitset-backed relations for small finite universes (arity at most 3)."""

from __future__ import annotations

from dataclasses import dataclass

from fopy.finite.relops import Relation


def _index_map(universe: list[int]) -> dict[int, int]:
    return {elem: idx for idx, elem in enumerate(universe)}


def _flat_index(indices: tuple[int, ...], sizes: tuple[int, ...]) -> int:
    flat = 0
    stride = 1
    for idx, size in zip(reversed(indices), reversed(sizes), strict=True):
        flat += idx * stride
        stride *= size
    return flat


@dataclass
class RelationBitset:
    """Compact relation storage using a Python integer bitset.

    Intended for arity ``<= 3`` and modest universe sizes where set/tuple
    membership tests dominate runtime. Universe elements are mapped to
    ``0 .. |U|-1`` via the supplied index table.

    Attributes:
        sym: Relation symbol (mirrors the source :class:`~fopy.finite.relops.Relation`).
        arity: Number of arguments (1, 2, or 3).
        universe_size: Cardinality of the indexed universe.
        bits: Bitset encoding membership of flattened argument tuples.
    """

    sym: str
    arity: int
    universe_size: int
    bits: int = 0

    @classmethod
    def from_relation(cls, rel: Relation, universe: list[int]) -> RelationBitset:
        """Build a bitset view of *rel* over *universe*.

        Args:
            rel: Source relation (arity must be at most 3).
            universe: Ordered domain used to map elements to bit positions.

        Returns:
            Bitset with the same extension as *rel* on *universe*.

        Raises:
            ValueError: If ``rel.arity > 3``.
        """
        if rel.arity > 3:
            raise ValueError("RelationBitset supports arity at most 3")
        index = _index_map(universe)
        obj = cls(sym=rel.sym, arity=rel.arity, universe_size=len(universe))
        for tup in rel.r:
            if all(elem in index for elem in tup):
                mapped = tuple(index[elem] for elem in tup)
                obj.add(mapped)
        return obj

    def to_relation(self) -> Relation:
        """Materialize a :class:`~fopy.finite.relops.Relation` from the bitset.

        Tuple arguments use indices ``0 .. universe_size - 1``.
        """
        rel = Relation.new(self.sym, self.arity)
        sizes = tuple(self.universe_size for _ in range(self.arity))
        limit = self.universe_size**self.arity
        for flat in range(limit):
            if self.bits & (1 << flat):
                tup = _unflatten(flat, sizes)
                rel.add(tup)
        return rel

    def add(self, args: tuple[int, ...]) -> None:
        """Insert one tuple into the bitset (indices, not universe values).

        Raises:
            ValueError: If ``len(args) != arity`` or an index is out of range.
        """
        if len(args) != self.arity:
            raise ValueError(f"Expected arity {self.arity}, got {len(args)}")
        sizes = tuple(self.universe_size for _ in range(self.arity))
        for idx in args:
            if not 0 <= idx < self.universe_size:
                raise ValueError(f"Index {idx} out of range for universe size {self.universe_size}")
        flat = _flat_index(args, sizes)
        self.bits |= 1 << flat

    def contains(self, args: tuple[int, ...]) -> bool:
        """Return whether *args* (as indices) belongs to the relation."""
        if len(args) != self.arity:
            return False
        sizes = tuple(self.universe_size for _ in range(self.arity))
        for idx in args:
            if not 0 <= idx < self.universe_size:
                return False
        flat = _flat_index(args, sizes)
        return bool(self.bits & (1 << flat))

    def __len__(self) -> int:
        """Return the number of tuples currently set."""
        return self.bits.bit_count()


def _unflatten(flat: int, sizes: tuple[int, ...]) -> tuple[int, ...]:
    result: list[int] = []
    for size in reversed(sizes):
        result.append(flat % size)
        flat //= size
    return tuple(reversed(result))
