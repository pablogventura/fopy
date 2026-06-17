"""Boolean simplification for formulas."""

from __future__ import annotations

from fopy.formulas import (
    And,
    Eq,
    Exists,
    FalseF,
    Formula,
    ForAll,
    Not,
    Or,
    TrueF,
    _and_formula,
    _neg,
    _or_formula,
)
from fopy.terms import Term


def eq(t1: Term, t2: Term) -> Formula:
    if t1 == t2:
        return TrueF()
    return Eq(t1, t2)


def true_formula() -> Formula:
    return TrueF()


def false_formula() -> Formula:
    return FalseF()


def and_formula(a: Formula, b: Formula) -> Formula:
    return _and_formula(a, b)


def or_formula(a: Formula, b: Formula) -> Formula:
    return _or_formula(a, b)


def neg(f: Formula) -> Formula:
    return _neg(f)


def simplify(f: Formula) -> Formula:
    if isinstance(f, Not):
        return _neg(simplify(f.arg))
    if isinstance(f, And):
        result = TrueF()
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
