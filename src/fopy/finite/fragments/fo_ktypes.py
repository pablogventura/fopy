"""First-order definability via bounded FO k-type partitions."""

from __future__ import annotations

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import partition_witness_formula
from fopy.finite.ktypes import fo_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def is_fo_definable(
    model: Model,
    target: Relation,
    *,
    max_k: int = 2,
) -> DefinabilityResult:
    """Decide FO-definability using bounded FO k-type partition refinement.

    Tuples are split by :func:`~fopy.finite.ktypes.fo_type` at quantifier rank
    *max_k*.  The target is FO-definable in this bounded sense exactly when the
    resulting partition is target-pure; a witness open formula is assembled as a
    disjunction of PP type conjunctions over positive blocks.

    Args:
        model: Finite algebra providing the signature.
        target: Relation whose definability is tested.
        max_k: Quantifier-rank bound forwarded to :func:`~fopy.finite.ktypes.fo_type`.

    Returns:
        :class:`~fopy.finite.definability.DefinabilityResult` with witness formula
        when definable, or obstruction tuples from a mixed block.

    Raises:
        ValueError: If tuple enumeration exceeds the partition size guard.
    """
    arity = target.arity
    partition = TuplePartition.from_model(model, arity)
    partition.refine(lambda row: fo_type(model, row, max_k, arity))
    if partition.is_target_pure(target):
        max_depth = max(arity, max_k)
        formula = partition_witness_formula(model, partition, target, max_depth=max_depth)
        return DefinabilityResult(definable=True, formula=formula, fragment="fo")
    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(definable=False, fragment="fo", witness_tuples=witnesses)
