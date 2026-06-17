"""Formula transformations: substitution, renaming."""

from __future__ import annotations

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
    _neg,
)
from fopy.simplify import simplify
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def free_vars(formula: Formula) -> set[Variable]:
    return formula.free_vars()


def bound_vars(formula: Formula) -> set[Variable]:
    return formula.bound_vars()


def _subst_term(t: Term, mapping: dict[Variable, Term]) -> Term:
    if isinstance(t, Variable):
        return mapping.get(t, t)
    if isinstance(t, Constant):
        return t
    if isinstance(t, Apply):
        return Apply(t.func, tuple(_subst_term(a, mapping) for a in t._args))
    return t


def _fresh_var(used: set[Variable], base: Variable) -> Variable:
    i = 0
    while True:
        v = Variable.from_index(i)
        if v not in used and v != base:
            return v
        i += 1


def substitute(formula: Formula, mapping: dict[Variable, Term]) -> Formula:
    """Capture-safe substitution."""
    if isinstance(formula, Variable):
        return mapping.get(formula, formula)  # type: ignore[return-value]

    if isinstance(formula, (TrueF, FalseF)):
        return formula

    if isinstance(formula, Atom):
        return Atom(formula.rel, tuple(_subst_term(a, mapping) for a in formula._args))

    if isinstance(formula, Eq):
        return Eq(_subst_term(formula.left, mapping), _subst_term(formula.right, mapping))

    if isinstance(formula, Not):
        return _neg(substitute(formula.arg, mapping))

    if isinstance(formula, And):
        return And(frozenset(substitute(c, mapping) for c in formula.children))

    if isinstance(formula, Or):
        return Or(frozenset(substitute(c, mapping) for c in formula.children))

    if isinstance(formula, (ForAll, Exists)):
        var = formula.var
        body = formula.body
        if var in mapping:
            used = body.free_vars() | set(mapping.keys())
            fresh = _fresh_var(used, var)
            body = substitute(body, {var: fresh})
            var = fresh
        new_body = substitute(body, {k: v for k, v in mapping.items() if k != var})
        if isinstance(formula, ForAll):
            return ForAll(var, new_body)
        return Exists(var, new_body)

    return formula


def subs(formula: Formula, mapping: dict[Variable, Term]) -> Formula:
    return simplify(substitute(formula, mapping))


def rename_bound(formula: Formula, var: Variable, new: Variable) -> Formula:
    """Rename bound occurrences of ``var`` to ``new`` (capture-safe)."""
    if isinstance(formula, (ForAll, Exists)) and formula.var == var:
        used = formula.body.free_vars() | formula.body.bound_vars() | {new}
        target = new if new not in used or new == var else _fresh_var(used, var)
        body = substitute(formula.body, {var: target})
        if isinstance(formula, ForAll):
            return ForAll(target, body)
        return Exists(target, body)
    if isinstance(formula, (TrueF, FalseF, Atom, Eq)):
        return formula
    if isinstance(formula, Not):
        return _neg(rename_bound(formula.arg, var, new))
    if isinstance(formula, And):
        return And(frozenset(rename_bound(c, var, new) for c in formula.children))
    if isinstance(formula, Or):
        return Or(frozenset(rename_bound(c, var, new) for c in formula.children))
    if isinstance(formula, ForAll):
        return ForAll(formula.var, rename_bound(formula.body, var, new))
    if isinstance(formula, Exists):
        return Exists(formula.var, rename_bound(formula.body, var, new))
    return formula
