"""First-order definability via bounded FO k-type partitions."""

from __future__ import annotations

from fopy.finite.definability import DefinabilityResult
from fopy.finite.eval_fast import try_fast_defining_check
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import partition_witness_formula
from fopy.finite.ktypes import fo_type
from fopy.finite.models import Model
from fopy.finite.relops import Relation
from fopy.solvers.z3_backend import z3_available


def _z3_auxiliary_verify(
    model: Model,
    target: Relation,
    formula: object,
) -> bool | None:
    """Cross-check a witness formula with fast eval and optional Z3 sanity."""
    from fopy.finite.open_formulas import Formula

    if not isinstance(formula, Formula):
        return None
    fast = try_fast_defining_check(model, formula, target)
    if fast is not None:
        return fast
    if not z3_available():
        return None
    ext = formula.extension(model, target.arity)
    return set(ext) == set(target.r)


def is_fo_definable(
    model: Model,
    target: Relation,
    *,
    max_k: int = 2,
    z3_crosscheck: bool = True,
) -> DefinabilityResult:
    """Decide FO-definability using bounded FO k-type partition refinement.

      Tuples are split by :func:`~fopy.finite.ktypes.fo_type` at quantifier rank
      *max_k*.  The target is FO-definable in this bounded sense exactly when the
      resulting partition is target-pure; a witness open formula is assembled as a
      disjunction of PP type conjunctions over positive blocks.

      When *z3_crosscheck* is ``True`` and a witness is found, an auxiliary fast
      path (bitset/numpy, then extension replay) confirms the formula matches
    *target*.

      Args:
          model: Finite algebra providing the signature.
          target: Relation whose definability is tested.
          max_k: Quantifier-rank bound forwarded to :func:`~fopy.finite.ktypes.fo_type`.
          z3_crosscheck: Run auxiliary verification on positive witnesses.

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
        if z3_crosscheck:
            verified = _z3_auxiliary_verify(model, target, formula)
            if verified is False:
                pair = partition.witness_pair(target)
                witnesses = [pair[0], pair[1]] if pair is not None else None
                return DefinabilityResult(definable=False, fragment="fo", witness_tuples=witnesses)
        return DefinabilityResult(definable=True, formula=formula, fragment="fo")
    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(definable=False, fragment="fo", witness_tuples=witnesses)
