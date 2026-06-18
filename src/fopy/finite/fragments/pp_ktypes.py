"""Primitive-positive definability via PP type partitions."""

from __future__ import annotations

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import partition_witness_formula
from fopy.finite.ktypes import atomic_pp_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def is_pp_definable(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 2,
) -> DefinabilityResult:
    """Decide PP-definability using primitive-positive type refinement.

      A relation is primitive-positive (PP) definable when it is a union of PP
      types: equivalently, when the partition of all arity-tuples refined by
      :func:`~fopy.finite.ktypes.atomic_pp_type` is *target-pure* (each block lies
    entirely inside or outside the target).

      Args:
          model: Finite algebra providing the signature.
          target: Relation whose open PP definability is tested.
          max_depth: Term depth bound passed to :func:`~fopy.finite.ktypes.atomic_pp_type`.

      Returns:
          :class:`~fopy.finite.definability.DefinabilityResult` with witness
          formula when definable, or obstruction tuples when not.

      Raises:
          ValueError: If tuple enumeration exceeds
              :data:`~fopy.finite.fragments._partition.MAX_TUPLE_PARTITION`.
    """
    partition = TuplePartition.from_model(model, target.arity)
    partition.refine(lambda row: atomic_pp_type(model, row, max_depth=max_depth))
    if partition.is_target_pure(target):
        formula = partition_witness_formula(model, partition, target, max_depth=max_depth)
        return DefinabilityResult(definable=True, formula=formula, fragment="pp")
    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(definable=False, fragment="pp", witness_tuples=witnesses)
