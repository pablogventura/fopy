"""Shared helpers for DefLab partition engines."""

from __future__ import annotations

import os
from dataclasses import dataclass

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import partition_witness_formula
from fopy.finite.models import Model
from fopy.finite.relops import Relation


@dataclass
class EngineMeta:
    """Metadata attached via DefinabilityResult.fragment naming."""

    engine: str
    complete_for_bound: bool
    reason: str = ""


def _want_formula() -> bool:
    return os.environ.get("FOPY_SKIP_WITNESS", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }


def result_yes(
    model: Model,
    partition: TuplePartition,
    target: Relation,
    *,
    fragment: str,
    engine: str,
    complete_for_bound: bool,
    max_depth: int = 2,
    synthesize_formula: bool | None = None,
) -> DefinabilityResult:
    """Positive verdict; set ``FOPY_SKIP_WITNESS=1`` to skip costly formula synthesis."""
    _ = complete_for_bound
    do_synth = _want_formula() if synthesize_formula is None else synthesize_formula
    formula = (
        partition_witness_formula(model, partition, target, max_depth=max_depth)
        if do_synth
        else None
    )
    return DefinabilityResult(
        definable=True,
        formula=formula,
        fragment=f"{fragment}:{engine}",
        witness_tuples=None,
    )


def result_no(
    partition: TuplePartition,
    target: Relation,
    *,
    fragment: str,
    engine: str,
) -> DefinabilityResult:
    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(
        definable=False,
        fragment=f"{fragment}:{engine}",
        witness_tuples=witnesses,
    )


def has_nontrivial_ops(model: Model) -> bool:
    """True if the model has a function symbol of arity >= 1."""
    return any(op.arity >= 1 for op in model.operations.values())
