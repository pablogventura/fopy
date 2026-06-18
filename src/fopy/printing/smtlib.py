"""SMT-LIB export for symbolic FO formulas."""

from __future__ import annotations

from typing import cast

from fopy.formulas import And, Atom, Eq, Exists, FalseF, ForAll, Formula, Not, Or, TrueF
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def to_smtlib(formula: Formula) -> str:
    """Export formula as SMT-LIB2 assertion."""
    return f"(assert {_formula_smt(formula)})"


def _formula_smt(f: Formula) -> str:
    if isinstance(f, TrueF):
        return "true"
    if isinstance(f, FalseF):
        return "false"
    if isinstance(f, Atom):
        args = " ".join(_term_smt(t) for t in f._args)
        return f"({f.rel} {args})" if args else f"({f.rel})"
    if isinstance(f, Eq):
        return f"(= {_term_smt(f.left)} {_term_smt(f.right)})"
    if isinstance(f, Not):
        return f"(not {_formula_smt(f.arg)})"
    if isinstance(f, And):
        parts = " ".join(_formula_smt(c) for c in f.children)
        return f"(and {parts})"
    if isinstance(f, Or):
        parts = " ".join(_formula_smt(c) for c in f.children)
        return f"(or {parts})"
    if isinstance(f, ForAll):
        return f"(forall (({_var_smt(f.var)} Int)) {_formula_smt(f.body)})"
    if isinstance(f, Exists):
        return f"(exists (({_var_smt(f.var)} Int)) {_formula_smt(f.body)})"
    return str(f)


def _term_smt(t: Term) -> str:
    if isinstance(t, Variable):
        return _var_smt(t)
    if isinstance(t, Constant):
        return t.name
    if isinstance(t, Apply):
        args = " ".join(_term_smt(cast(Term, a)) for a in t._args)
        return f"({t.func} {args})"
    return str(t)


def _var_smt(v: Variable) -> str:
    return v.sym.replace("₀", "0").replace("₁", "1")
