"""Positive open split: refine by positive equality diagrams."""

from __future__ import annotations

from fopy.engines._common import has_nontrivial_ops, result_no, result_yes
from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def positive_eq_diagram_key(row: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    """Equality pattern: pairs (i, j) with row[i] == row[j]."""
    k = len(row)
    return frozenset((i, j) for i in range(k) for j in range(k) if row[i] == row[j])


def check_positive_split(model: Model, target: Relation) -> DefinabilityResult:
    """Split by ``SamePositiveEqDiagram`` (Lean: PositiveSplit).

    Complete when the signature has no nontrivial function symbols (NoFunctions
    case). With operations, purity is still a sound *sufficient* condition for
    a positive equality-diagram certificate, but incompleteness is flagged in
    the fragment label.
    """
    partition = TuplePartition.from_model(model, target.arity)
    partition.refine(positive_eq_diagram_key)
    engine = "positive_split"
    fragment = "qf_pos"
    if partition.is_target_pure(target):
        return result_yes(
            model,
            partition,
            target,
            fragment=fragment,
            engine=engine if not has_nontrivial_ops(model) else f"{engine}_ops_partial",
            complete_for_bound=not has_nontrivial_ops(model),
        )
    return result_no(partition, target, fragment=fragment, engine=engine)
