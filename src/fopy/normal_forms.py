"""Prenex and NNF normal forms for symbolic FO formulas."""

from __future__ import annotations

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
    _neg,
)
from fopy.symbols import Variable


def to_nnf(formula: Formula) -> Formula:
    """Convert a formula to negation normal form (NNF).

    Pushes negations inward using De Morgan laws and flips quantifiers under
    negation. The result contains ``Not`` only immediately above atoms or equalities.

    Args:
        formula: Arbitrary first-order formula over :mod:`fopy.formulas`.

    Returns:
        An equivalent formula in NNF.
    """
    if isinstance(formula, (TrueF, FalseF, Atom, Eq)):
        return formula
    if isinstance(formula, Not):
        inner = formula.arg
        if isinstance(inner, Not):
            return to_nnf(inner.arg)
        if isinstance(inner, And):
            return Or(frozenset(to_nnf(_neg(c)) for c in inner.children))
        if isinstance(inner, Or):
            return And(frozenset(to_nnf(_neg(c)) for c in inner.children))
        if isinstance(inner, ForAll):
            return Exists(inner.var, to_nnf(_neg(inner.body)))
        if isinstance(inner, Exists):
            return ForAll(inner.var, to_nnf(_neg(inner.body)))
        return Not(to_nnf(inner))
    if isinstance(formula, And):
        return And(frozenset(to_nnf(c) for c in formula.children))
    if isinstance(formula, Or):
        return Or(frozenset(to_nnf(c) for c in formula.children))
    if isinstance(formula, ForAll):
        return ForAll(formula.var, to_nnf(formula.body))
    if isinstance(formula, Exists):
        return Exists(formula.var, to_nnf(formula.body))
    return formula


def to_prenex(formula: Formula) -> Formula:
    """Convert a formula to prenex normal form.

    All quantifiers appear outermost after converting to NNF internally.
    Free-variable semantics are preserved.

    Args:
        formula: Input formula.

    Returns:
        An equivalent formula ``Q1 x1 … Qk xk φ`` with ``φ`` quantifier-free.
    """
    return _prenex(to_nnf(formula), [], [])


def _prenex(
    formula: Formula,
    prefix_forall: list[Variable],
    prefix_exists: list[Variable],
) -> Formula:
    if isinstance(formula, (TrueF, FalseF, Atom, Eq)):
        body: Formula = formula
        for v in reversed(prefix_exists):
            body = Exists(v, body)
        for v in reversed(prefix_forall):
            body = ForAll(v, body)
        return body
    if isinstance(formula, And):
        return _prenex_helper(formula.children, prefix_forall, prefix_exists, And)
    if isinstance(formula, Or):
        return _prenex_helper(formula.children, prefix_forall, prefix_exists, Or)
    if isinstance(formula, ForAll):
        return _prenex(formula.body, prefix_forall + [formula.var], prefix_exists)
    if isinstance(formula, Exists):
        return _prenex(formula.body, prefix_forall, prefix_exists + [formula.var])
    return formula


def _prenex_helper(
    children: frozenset[Formula],
    prefix_forall: list[Variable],
    prefix_exists: list[Variable],
    combiner: type[And] | type[Or],
) -> Formula:
    parts = [_prenex(c, prefix_forall, prefix_exists) for c in children]
    return combiner(frozenset(parts))


def to_cnf(formula: Formula) -> Formula:
    """Convert a formula to conjunctive normal form (CNF).

    Applies distributivity to an NNF input so the result is a conjunction of
    disjunctions of literals.

    Args:
        formula: Arbitrary first-order formula.

    Returns:
        An equivalent formula in CNF.
    """
    return _cnf(to_nnf(formula))


def to_dnf(formula: Formula) -> Formula:
    """Convert a formula to disjunctive normal form (DNF).

    Applies distributivity to an NNF input so the result is a disjunction of
    conjunctions of literals.

    Args:
        formula: Arbitrary first-order formula.

    Returns:
        An equivalent formula in DNF.
    """
    return _dnf(to_nnf(formula))


def _cnf(formula: Formula) -> Formula:
    if isinstance(formula, And):
        parts: list[Formula] = []
        for child in formula.children:
            cnf_child = _cnf(child)
            if isinstance(cnf_child, And):
                parts.extend(cnf_child.children)
            else:
                parts.append(cnf_child)
        return And(frozenset(parts))
    if isinstance(formula, Or):
        parts = list(formula.children)
        acc = parts[0]
        for other in parts[1:]:
            acc = _distribute_or_cnf(acc, other)
        return _cnf(acc)
    return formula


def _dnf(formula: Formula) -> Formula:
    if isinstance(formula, Or):
        parts: list[Formula] = []
        for child in formula.children:
            dnf_child = _dnf(child)
            if isinstance(dnf_child, Or):
                parts.extend(dnf_child.children)
            else:
                parts.append(dnf_child)
        return Or(frozenset(parts))
    if isinstance(formula, And):
        parts = list(formula.children)
        acc = parts[0]
        for other in parts[1:]:
            acc = _distribute_and_dnf(acc, other)
        return _dnf(acc)
    return formula


def _distribute_or_cnf(left: Formula, right: Formula) -> Formula:
    if isinstance(left, And):
        return And(frozenset(_distribute_or_cnf(child, right) for child in left.children))
    if isinstance(right, And):
        return And(frozenset(_distribute_or_cnf(left, child) for child in right.children))
    return Or(frozenset({left, right}))


def _distribute_and_dnf(left: Formula, right: Formula) -> Formula:
    if isinstance(left, Or):
        return Or(frozenset(_distribute_and_dnf(child, right) for child in left.children))
    if isinstance(right, Or):
        return Or(frozenset(_distribute_and_dnf(left, child) for child in right.children))
    return And(frozenset({left, right}))
