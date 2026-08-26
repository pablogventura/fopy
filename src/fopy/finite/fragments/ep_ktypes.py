"""Existential-positive definability via PP types."""

from __future__ import annotations

from itertools import product

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import partition_witness_formula
from fopy.finite.ktypes import atomic_pp_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def _equality_pattern(row: tuple[int, ...]) -> tuple[int, ...]:
    """Pairwise equality bits for *row* (i < j)."""
    bits: list[int] = []
    for i in range(len(row)):
        for j in range(i + 1, len(row)):
            bits.append(1 if row[i] == row[j] else 0)
    return tuple(bits)


def _ep_matrix_type(
    model: Model,
    row: tuple[int, ...],
    *,
    max_depth: int,
) -> tuple[object, ...]:
    """PP type, or equality pattern when the operational signature is empty.

    Absolute element ids are not EP-definable without constants/ops; using them
    as the type key over-accepts (every singleton block looks pure).
    """
    if not model.operations:
        return _equality_pattern(row)
    return atomic_pp_type(model, row, max_depth=max_depth)


def _ep_type_key(
    model: Model,
    row: tuple[int, ...],
    *,
    max_depth: int,
    max_existentials: int = 1,
) -> tuple[object, ...]:
    """Refine a matrix type with bounded existential extensions over the universe."""
    base = _ep_matrix_type(model, row, max_depth=max_depth)
    extensions: list[tuple[object, ...]] = []
    universe = model.universe
    for _m in range(1, max_existentials + 1):
        for extra in product(universe, repeat=_m):
            extended = row + extra
            extensions.append(_ep_matrix_type(model, extended, max_depth=max_depth))
    return (base, tuple(sorted(extensions)))


def is_ep_definable(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 2,
    max_existentials: int = 1,
) -> DefinabilityResult:
    """Decide existential-positive definability using PP type refinement.

    Existential-positive (EP) formulas allow existentially quantified variables
    before a primitive-positive matrix.  This checker refines matrix types by the
    multiset of types of bounded existential extensions (adding up to
    *max_existentials* fresh coordinates ranging over the universe).

    When the model has no operations, the matrix type is the equality pattern of
    the tuple (parity with Rust ``ep_type``), not absolute element ids.

    Args:
        model: Finite algebra providing the signature.
        target: Relation to test.
        max_depth: Term depth for underlying PP types.
        max_existentials: Maximum number of existentially quantified coordinates
            used during refinement.

    Returns:
        :class:`~fopy.finite.definability.DefinabilityResult` with witness when
        definable in the bounded EP fragment, or obstruction tuples otherwise.

    Raises:
        ValueError: If tuple enumeration exceeds the partition size guard.
    """
    partition = TuplePartition.from_model(model, target.arity)

    def key(row: tuple[int, ...]) -> tuple[object, ...]:
        return _ep_type_key(model, row, max_depth=max_depth, max_existentials=max_existentials)

    partition.refine(key)
    if partition.is_target_pure(target):
        formula = partition_witness_formula(model, partition, target, max_depth=max_depth)
        return DefinabilityResult(definable=True, formula=formula, fragment="ep")
    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(definable=False, fragment="ep", witness_tuples=witnesses)
