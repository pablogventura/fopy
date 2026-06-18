"""Witness formula construction from tuple partitions."""

from __future__ import annotations

from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.models import Model
from fopy.finite.open_formulas import (
    Formula,
    OpSym,
    Term,
    Variable,
    eq,
    false_formula,
    true_formula,
)
from fopy.finite.relops import Operation, Relation


def _term_arg_tuples(terms: list[Term], arity: int) -> list[tuple[Term, ...]]:
    if arity == 0:
        return [()]
    if arity == 1:
        return [(t,) for t in terms]
    result: list[tuple[Term, ...]] = [()]
    for _ in range(arity):
        result = [r + (t,) for r in result for t in terms]
    return result


def _enumerate_terms(arity: int, operations: dict[str, Operation], max_depth: int) -> list[Term]:
    ops_by_arity: dict[int, list[str]] = {}
    for sym, op in operations.items():
        ops_by_arity.setdefault(op.arity, []).append(sym)
    for syms in ops_by_arity.values():
        syms.sort()

    terms: list[Term] = [Term.from_variable(Variable.from_index(i)) for i in range(arity)]
    ordered: list[Term] = []
    for depth in range(max_depth + 1):
        current = [t for t in terms if t.grade() == depth]
        current.sort(key=str)
        ordered.extend(current)
        if depth == max_depth:
            break
        next_terms: list[Term] = []
        for ar, syms in sorted(ops_by_arity.items()):
            if ar == 0:
                continue
            for sym in syms:
                for args in _term_arg_tuples(terms, ar):
                    next_terms.append(Term.op_term(OpSym.new(sym, ar), list(args)))
        terms.extend(next_terms)
    return ordered


def type_conjunction_formula(
    model: Model,
    representative: tuple[int, ...],
    *,
    max_depth: int,
) -> Formula:
    """Build a conjunction of term equalities characterising one PP type.

    Args:
        model: Finite model for evaluation and signature.
        representative: Witness tuple for the type block.
        max_depth: Term depth bound (matches PP typing).

    Returns:
        Conjunctive open formula over equalities between terms that coincide on
        *representative*.
    """
    arity = len(representative)
    vector = {Variable.from_index(i): representative[i] for i in range(arity)}
    terms = _enumerate_terms(arity, model.operations, max_depth)
    evaluations: list[int | None] = []
    for term in terms:
        try:
            evaluations.append(term.evaluate(model.operations, vector))
        except (KeyError, ValueError):
            evaluations.append(None)
    conj: Formula | None = None
    for i, left in enumerate(terms):
        for j in range(i + 1, len(terms)):
            if evaluations[i] is None or evaluations[i] != evaluations[j]:
                continue
            atom = eq(left, terms[j])
            conj = atom if conj is None else conj.and_formula(atom)
    if conj is None:
        return true_formula({Variable.from_index(i) for i in range(arity)})
    return conj


def partition_witness_formula(
    model: Model,
    partition: TuplePartition,
    target: Relation,
    *,
    max_depth: int,
) -> Formula:
    """Assemble a disjunctive normal form formula from a target-pure partition.

    Each positive block contributes one disjunct: the PP type formula of a
    representative tuple.  Negative-only blocks are skipped.

    Args:
        model: Finite model used for term evaluation.
        partition: Refined partition that is target-pure.
        target: Target relation (must be constant on each block).
        max_depth: Term depth for type formulas.

    Returns:
        Disjunctive witness formula over positive blocks.
    """
    disjuncts: list[Formula] = []
    for block in partition.blocks:
        rep = next(iter(block))
        if not target.contains(rep):
            continue
        disjuncts.append(type_conjunction_formula(model, rep, max_depth=max_depth))
    if not disjuncts:
        return false_formula({Variable.from_index(i) for i in range(target.arity)})
    result = disjuncts[0]
    for part in disjuncts[1:]:
        result = result.or_formula(part)
    return result
