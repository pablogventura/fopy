"""Horn definability via bounded clause witness search."""

from __future__ import annotations

from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.fragments._witness import _enumerate_terms, partition_witness_formula
from fopy.finite.fragments.pp_ktypes import is_pp_definable
from fopy.finite.ktypes import atomic_pp_type
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, eq
from fopy.finite.relops import Relation


def _horn_clause_candidates(
    model: Model,
    arity: int,
    *,
    max_depth: int,
    max_atoms: int,
) -> list[Formula]:
    """Enumerate small Horn clauses ``(⋀ antecedent) → consequent`` as formulas.

      Each atom is an equality between terms over the first *arity* variables.
    The consequent is a single term equality; antecedents are bounded in length.
    """
    terms = _enumerate_terms(arity, model.operations, max_depth)
    atoms = [eq(t1, t2) for t1 in terms for t2 in terms if str(t1) <= str(t2)]
    clauses: list[Formula] = []
    for cons in atoms:
        clauses.append(cons)
        for left in atoms:
            if left == cons:
                continue
            clauses.append(_implication_formula(left, cons))
            if max_atoms >= 2:
                for right in atoms:
                    if right in {left, cons}:
                        continue
                    ant = left.and_formula(right)
                    clauses.append(_implication_formula(ant, cons))
    return clauses


def _implication_formula(antecedent: Formula, consequent: Formula) -> Formula:
    """Encode ``antecedent -> consequent`` as ``(not antecedent) or consequent``."""
    return antecedent.neg().or_formula(consequent)


def _extension_matches_target(model: Model, target: Relation, formula: Formula) -> bool:
    try:
        ext = formula.extension(model, target.arity)
    except (KeyError, ValueError):
        return False
    return ext == set(target.r)


def is_horn_definable(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 2,
    max_clauses: int = 4,
    max_atoms: int = 2,
) -> DefinabilityResult:
    """Decide Horn definability with bounded Horn clause witness search.

    First checks whether the target is already PP-definable (PP formulas are
    Horn).  Otherwise searches for a conjunction of short Horn clauses whose
    extension matches the target on *model*.

    Args:
        model: Finite algebra providing the signature.
        target: Relation to define.
        max_depth: Term depth for atoms in candidate clauses.
        max_clauses: Maximum number of Horn clauses in a candidate definition.
        max_atoms: Maximum antecedent length (per clause) during enumeration.

    Returns:
        :class:`~fopy.finite.definability.DefinabilityResult` with a Horn
        witness when found, or obstruction tuples from the PP-type partition.

    Raises:
        ValueError: If tuple enumeration exceeds the partition size guard.
    """
    pp = is_pp_definable(model, target, max_depth=max_depth)
    if pp.definable:
        return DefinabilityResult(
            definable=True,
            formula=pp.formula,
            fragment="horn",
        )

    partition = TuplePartition.from_model(model, target.arity)
    partition.refine(lambda row: atomic_pp_type(model, row, max_depth=max_depth))
    if not partition.is_target_pure(target):
        pair = partition.witness_pair(target)
        witnesses = [pair[0], pair[1]] if pair is not None else None
        return DefinabilityResult(definable=False, fragment="horn", witness_tuples=witnesses)

    candidates = _horn_clause_candidates(
        model, target.arity, max_depth=max_depth, max_atoms=max_atoms
    )
    for clause in candidates:
        if _extension_matches_target(model, target, clause):
            return DefinabilityResult(definable=True, formula=clause, fragment="horn")

    if max_clauses >= 2:
        limit = min(len(candidates), 24)
        for i in range(limit):
            for j in range(i + 1, limit):
                trial = candidates[i].and_formula(candidates[j])
                if _extension_matches_target(model, target, trial):
                    return DefinabilityResult(definable=True, formula=trial, fragment="horn")

    formula = partition_witness_formula(model, partition, target, max_depth=max_depth)
    if _extension_matches_target(model, target, formula):
        return DefinabilityResult(definable=True, formula=formula, fragment="horn")

    pair = partition.witness_pair(target)
    witnesses = [pair[0], pair[1]] if pair is not None else None
    return DefinabilityResult(definable=False, fragment="horn", witness_tuples=witnesses)
