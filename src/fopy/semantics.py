"""Evaluation and satisfaction."""

from __future__ import annotations

from itertools import product
from typing import Any, cast

from fopy.formulas import (
    And,
    Atom,
    Eq,
    Exists,
    FalseF,
    ForAll,
    Formula,
    Not,
    Or,
    TrueF,
)
from fopy.sorts import DEFAULT_SORT, Sort
from fopy.structures import Structure
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def sort_carrier(structure: Structure, sort: Sort | str = DEFAULT_SORT) -> list[Any]:
    """Return the universe carrier for *sort* on *structure*."""
    return structure.universe_for(sort)


def evaluate(term: Term, structure: Structure, assignment: dict[Variable, Any]) -> Any:
    """Evaluate a term in a structure under a variable assignment.

    Args:
        term: Term to evaluate.
        structure: Structure providing function interpretations.
        assignment: Map from variables to universe elements.

    Returns:
        The value of *term* in *structure* under *assignment*.

    Raises:
        ValueError: If a variable in *term* is not bound in *assignment*.
        TypeError: If *term* is not a supported term node.
    """
    if isinstance(term, Variable):
        if term not in assignment:
            raise ValueError(f"Unbound variable {term}")
        return assignment[term]
    if isinstance(term, Constant):
        return structure.call_function(term.name, ())
    if isinstance(term, Apply):
        args = tuple(evaluate(cast(Term, a), structure, assignment) for a in term._args)
        return structure.call_function(term.func, args)
    raise TypeError(type(term))


def satisfy(
    formula: Formula,
    structure: Structure,
    assignment: dict[Variable, Any] | None = None,
) -> bool:
    """Decide whether a formula holds in a structure under an assignment.

    Args:
        formula: Formula to test.
        structure: Structure providing universe and interpretations.
        assignment: Optional map from free variables to universe elements.

    Returns:
        ``True`` if *formula* is satisfied, ``False`` otherwise.

    Raises:
        TypeError: If *formula* is not a supported formula node.
    """
    assignment = dict(assignment or {})

    if isinstance(formula, TrueF):
        return True
    if isinstance(formula, FalseF):
        return False
    if isinstance(formula, Atom):
        args = tuple(evaluate(a, structure, assignment) for a in formula._args)
        return bool(structure.call_relation(formula.rel, args))
    if isinstance(formula, Eq):
        return bool(
            evaluate(formula.left, structure, assignment)
            == evaluate(formula.right, structure, assignment)
        )
    if isinstance(formula, Not):
        return not satisfy(formula.arg, structure, assignment)
    if isinstance(formula, And):
        return all(satisfy(c, structure, assignment) for c in formula.children)
    if isinstance(formula, Or):
        return any(satisfy(c, structure, assignment) for c in formula.children)
    if isinstance(formula, ForAll):
        var = formula.var
        carrier = sort_carrier(structure, var.sort)
        for elem in carrier:
            new_assign = dict(assignment)
            new_assign[var] = elem
            if not satisfy(formula.body, structure, new_assign):
                return False
        return True
    if isinstance(formula, Exists):
        var = formula.var
        carrier = sort_carrier(structure, var.sort)
        for elem in carrier:
            new_assign = dict(assignment)
            new_assign[var] = elem
            if satisfy(formula.body, structure, new_assign):
                return True
        return False
    raise TypeError(type(formula))


def extension(
    formula: Formula,
    structure: Structure,
    arity: int,
    variables: list[Variable] | None = None,
) -> set[tuple[Any, ...]]:
    """Compute the extension of a quantifier-free formula as a relation.

    Args:
        formula: Quantifier-free formula over *variables*.
        structure: Structure used for evaluation.
        arity: Number of free variables when *variables* is omitted.
        variables: Optional ordered list of free variables; defaults to
            ``Variable.from_index(0)``, …, ``Variable.from_index(arity - 1)``.

    Returns:
        Set of variable assignments (as tuples) on which *formula* holds.
    """
    if variables is None:
        variables = [Variable.from_index(i) for i in range(arity)]
    carriers = [sort_carrier(structure, v.sort) for v in variables]
    result: set[tuple[Any, ...]] = set()
    for tup in product(*carriers):
        assign = dict(zip(variables, tup, strict=True))
        if satisfy(formula, structure, assign):
            result.add(tup)
    return result
