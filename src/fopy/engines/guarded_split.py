"""Guarded-fragment style split: FO-k types with guarded label (bound)."""

from __future__ import annotations

from fopy.engines._common import result_no, result_yes
from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.ktypes import fo_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def check_guarded(
    model: Model,
    target: Relation,
    *,
    max_k: int = 1,
) -> DefinabilityResult:
    """Bounded guarded-inspired split.

    Uses FO-type refinement at low quantifier rank as a stand-in for guarded
    types on tiny models (inspire: Jung-Wolter / Hoogland). Complete only for
    the chosen bound; Lean residual tracks the real GF characterization.
    """
    arity = target.arity
    partition = TuplePartition.from_model(model, arity)
    partition.refine(lambda row: fo_type(model, row, max_k, arity))
    if partition.is_target_pure(target):
        return result_yes(
            model,
            partition,
            target,
            fragment="gf",
            engine=f"guarded_split_k{max_k}",
            complete_for_bound=True,
            max_depth=max_k,
        )
    return result_no(partition, target, fragment="gf", engine=f"guarded_split_k{max_k}")
