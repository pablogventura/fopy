"""Formula transformations: substitution, renaming."""

from __future__ import annotations

from typing import cast

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
from fopy.simplify import simplify
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def free_vars(formula: Formula) -> set[Variable]:
    """Return the set of free variables in *formula*.

    Args:
        formula: Formula to inspect.

    Returns:
        Free variables occurring in *formula*.
    """
    return formula.free_vars()


def bound_vars(formula: Formula) -> set[Variable]:
    """Return the set of bound variables in *formula*.

    Args:
        formula: Formula to inspect.

    Returns:
        Bound variables occurring in *formula*.
    """
    return formula.bound_vars()


def _subst_term(t: Term, mapping: dict[Variable, Term]) -> Term:
    if isinstance(t, Variable):
        return mapping.get(t, t)
    if isinstance(t, Constant):
        return t
    if isinstance(t, Apply):
        return Apply(t.func, tuple(_subst_term(cast(Term, a), mapping) for a in t._args))
    return t


def _fresh_var(used: set[Variable], base: Variable) -> Variable:
    i = 0
    while True:
        v = Variable.from_index(i)
        if v not in used and v != base:
            return v
        i += 1


def substitute(formula: Formula, mapping: dict[Variable, Term]) -> Formula:
    """Apply capture-safe substitution of terms for variables.

    Args:
        formula: Formula to transform.
        mapping: Map from variables to replacement terms.

    Returns:
        Formula obtained by substituting according to *mapping*.
    """
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
            body = substitute(body, {var: cast(Term, fresh)})
            var = fresh
        new_body = substitute(body, {k: v for k, v in mapping.items() if k != var})
        if isinstance(formula, ForAll):
            return ForAll(var, new_body)
        return Exists(var, new_body)

    return formula


def subs(formula: Formula, mapping: dict[Variable, Term]) -> Formula:
    """Substitute and simplify a formula.

    Args:
        formula: Formula to transform.
        mapping: Map from variables to replacement terms.

    Returns:
        Simplified result of :func:`substitute`.
    """
    return simplify(substitute(formula, mapping))


def rename_bound(formula: Formula, var: Variable, new: Variable) -> Formula:
    """Rename bound occurrences of *var* to *new* (capture-safe).

    Args:
        formula: Formula to transform.
        var: Bound variable to rename.
        new: Replacement variable name.

    Returns:
        Formula with bound occurrences of *var* renamed to *new*.
    """
    if isinstance(formula, (ForAll, Exists)) and formula.var == var:
        used = formula.body.free_vars() | formula.body.bound_vars() | {new}
        target = new if new not in used or new == var else _fresh_var(used, var)
        body = substitute(formula.body, {var: cast(Term, target)})
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


def alpha_equivalent(left: Formula, right: Formula) -> bool:
    """Return whether *left* and *right* are alpha-equivalent.

    Renames bound variables of each formula to canonical fresh names, then
    compares structural equality after simplification.

    Args:
        left: First formula.
        right: Second formula.

    Returns:
        ``True`` when the formulas differ only by bound variable names.
    """
    return simplify(_alpha_normalize(left)) == simplify(_alpha_normalize(right))


def _alpha_normalize(formula: Formula) -> Formula:
    """Rename all variables to canonical ``__v{n}`` in first-occurrence order."""
    mapping: dict[Variable, Variable] = {}
    counter = 0

    def canon(v: Variable) -> Variable:
        nonlocal counter
        if v not in mapping:
            mapping[v] = Variable(f"__v{counter}", v.sort)
            counter += 1
        return mapping[v]

    def on_term(t: Term) -> Term:
        if isinstance(t, Variable):
            return cast(Term, canon(t))
        if isinstance(t, Constant):
            return t
        if isinstance(t, Apply):
            return Apply(t.func, tuple(on_term(cast(Term, a)) for a in t._args))
        return t

    def norm(f: Formula) -> Formula:
        if isinstance(f, (TrueF, FalseF)):
            return f
        if isinstance(f, Variable):
            return canon(f)  # type: ignore[return-value]
        if isinstance(f, Atom):
            return Atom(f.rel, tuple(on_term(a) for a in f._args))
        if isinstance(f, Eq):
            return Eq(on_term(f.left), on_term(f.right))
        if isinstance(f, Not):
            return _neg(norm(f.arg))
        if isinstance(f, And):
            return And(frozenset(norm(c) for c in f.children))
        if isinstance(f, Or):
            return Or(frozenset(norm(c) for c in f.children))
        if isinstance(f, ForAll):
            body = substitute(f.body, {f.var: cast(Term, canon(f.var))})
            return ForAll(canon(f.var), norm(body))
        if isinstance(f, Exists):
            body = substitute(f.body, {f.var: cast(Term, canon(f.var))})
            return Exists(canon(f.var), norm(body))
        return f

    return norm(formula)
