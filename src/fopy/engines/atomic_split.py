"""Atomic / PP signature splitting."""

from __future__ import annotations

from fopy.engines._common import result_no, result_yes
from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.ktypes import atomic_pp_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def check_pp_split(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 2,
) -> DefinabilityResult:
    """PP split by atomic PP-types (same as k-types, labeled as split engine)."""
    partition = TuplePartition.from_model(model, target.arity)
    partition.refine(lambda row: atomic_pp_type(model, row, max_depth=max_depth))
    if partition.is_target_pure(target):
        return result_yes(
            model,
            partition,
            target,
            fragment="pp",
            engine=f"pp_split_d{max_depth}",
            complete_for_bound=True,
            max_depth=max_depth,
        )
    return result_no(partition, target, fragment="pp", engine=f"pp_split_d{max_depth}")


def check_atomic_conj(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 1,
) -> DefinabilityResult:
    """Atomic-conjunction split: shallow PP-type (depth 1 default)."""
    partition = TuplePartition.from_model(model, target.arity)
    partition.refine(lambda row: atomic_pp_type(model, row, max_depth=max_depth))
    if partition.is_target_pure(target):
        return result_yes(
            model,
            partition,
            target,
            fragment="atomic_conj",
            engine=f"atomic_split_d{max_depth}",
            complete_for_bound=True,
            max_depth=max_depth,
        )
    return result_no(
        partition, target, fragment="atomic_conj", engine=f"atomic_split_d{max_depth}"
    )
