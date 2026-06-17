"""Evaluation and satisfaction."""

from __future__ import annotations

from itertools import product
from typing import Any

from fopy.formulas import (
    And,
    Atom,
    Eq,
    Exists,
    FalseF,
    Formula,
    ForAll,
    Not,
    Or,
    TrueF,
)
from fopy.structures import Structure
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def evaluate(term: Term, structure: Structure, assignment: dict[Variable, Any]) -> Any:
    if isinstance(term, Variable):
        if term not in assignment:
            raise ValueError(f"Unbound variable {term}")
        return assignment[term]
    if isinstance(term, Constant):
        return structure.call_function(term.name, ())
    if isinstance(term, Apply):
        args = tuple(evaluate(a, structure, assignment) for a in term._args)
        return structure.call_function(term.func, args)
    raise TypeError(type(term))


def satisfy(formula: Formula, structure: Structure, assignment: dict[Variable, Any] | None = None) -> bool:
    assignment = dict(assignment or {})

    if isinstance(formula, TrueF):
        return True
    if isinstance(formula, FalseF):
        return False
    if isinstance(formula, Atom):
        args = tuple(evaluate(a, structure, assignment) for a in formula._args)
        return structure.call_relation(formula.rel, args)
    if isinstance(formula, Eq):
        return evaluate(formula.left, structure, assignment) == evaluate(
            formula.right, structure, assignment
        )
    if isinstance(formula, Not):
        return not satisfy(formula.arg, structure, assignment)
    if isinstance(formula, And):
        return all(satisfy(c, structure, assignment) for c in formula.children)
    if isinstance(formula, Or):
        return any(satisfy(c, structure, assignment) for c in formula.children)
    if isinstance(formula, ForAll):
        var = formula.var
        for elem in structure.universe:
            new_assign = dict(assignment)
            new_assign[var] = elem
            if not satisfy(formula.body, structure, new_assign):
                return False
        return True
    if isinstance(formula, Exists):
        var = formula.var
        for elem in structure.universe:
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
    """Extensional relation of a quantifier-free formula."""
    if variables is None:
        variables = [Variable.from_index(i) for i in range(arity)]
    result: set[tuple[Any, ...]] = set()
    for tup in product(structure.universe, repeat=len(variables)):
        assign = dict(zip(variables, tup))
        if satisfy(formula, structure, assign):
            result.add(tup)
    return result
