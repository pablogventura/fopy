"""Boolean simplification for formulas."""

from __future__ import annotations

from fopy.formulas import (
    And,
    Eq,
    Exists,
    FalseF,
    ForAll,
    Formula,
    Not,
    Or,
    TrueF,
    _and_formula,
    _neg,
    _or_formula,
)
from fopy.terms import Term


def eq(t1: Term, t2: Term) -> Formula:
    """Build an equality formula, simplifying reflexive equalities to true.

    Args:
        t1: Left-hand side term.
        t2: Right-hand side term.

    Returns:
        :class:`~fopy.formulas.Eq` formula, or :class:`~fopy.formulas.TrueF`
        when *t1* and *t2* are identical.
    """
    if t1 == t2:
        return TrueF()
    return Eq(t1, t2)


def true_formula() -> Formula:
    """Return the true formula constant."""
    return TrueF()


def false_formula() -> Formula:
    """Return the false formula constant."""
    return FalseF()


def and_formula(a: Formula, b: Formula) -> Formula:
    """Build a conjunction, applying boolean simplification rules.

    Args:
        a: Left conjunct.
        b: Right conjunct.

    Returns:
        Simplified conjunction of *a* and *b*.
    """
    return _and_formula(a, b)


def or_formula(a: Formula, b: Formula) -> Formula:
    """Build a disjunction, applying boolean simplification rules.

    Args:
        a: Left disjunct.
        b: Right disjunct.

    Returns:
        Simplified disjunction of *a* and *b*.
    """
    return _or_formula(a, b)


def neg(f: Formula) -> Formula:
    """Negate a formula, applying boolean simplification rules.

    Args:
        f: Formula to negate.

    Returns:
        Simplified negation of *f*.
    """
    return _neg(f)


def simplify(f: Formula) -> Formula:
    """Recursively simplify a formula using boolean identities.

    Args:
        f: Formula to simplify.

    Returns:
        Structurally simplified formula.
    """
    if isinstance(f, Not):
        return _neg(simplify(f.arg))
    if isinstance(f, And):
        result: Formula = TrueF()
        for c in sorted(f.children, key=repr):
            result = _and_formula(result, simplify(c))
        return result
    if isinstance(f, Or):
        result = FalseF()
        for c in sorted(f.children, key=repr):
            result = _or_formula(result, simplify(c))
        return result
    if isinstance(f, ForAll):
        return ForAll(f.var, simplify(f.body))
    if isinstance(f, Exists):
        return Exists(f.var, simplify(f.body))
    if isinstance(f, Eq):
        if f.left == f.right:
            return TrueF()
        return f
    return f
