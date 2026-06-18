"""TPTP export for symbolic FO formulas."""

from __future__ import annotations

from typing import cast

from fopy.formulas import And, Atom, Eq, Exists, FalseF, ForAll, Formula, Not, Or, TrueF
from fopy.sorts import DEFAULT_SORT
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def to_tptp(formula: Formula, name: str = "conjecture") -> str:
    """Export a formula as TPTP CNF-style fof."""
    body = _formula_tptp(formula)
    return f"fof({name}, conjecture, {body})."


def _formula_tptp(f: Formula) -> str:
    if isinstance(f, TrueF):
        return "$true"
    if isinstance(f, FalseF):
        return "$false"
    if isinstance(f, Atom):
        args = ", ".join(_term_tptp(t) for t in f._args)
        return f"{f.rel}({args})" if args else f"{f.rel}"
    if isinstance(f, Eq):
        return f"({_term_tptp(f.left)} = {_term_tptp(f.right)})"
    if isinstance(f, Not):
        return f"~({_formula_tptp(f.arg)})"
    if isinstance(f, And):
        parts = " & ".join(_formula_tptp(c) for c in sorted(f.children, key=repr))
        return f"({parts})"
    if isinstance(f, Or):
        parts = " | ".join(_formula_tptp(c) for c in sorted(f.children, key=repr))
        return f"({parts})"
    if isinstance(f, ForAll):
        return f"![{_var_tptp(f.var)}]: ({_formula_tptp(f.body)})"
    if isinstance(f, Exists):
        return f"?[{_var_tptp(f.var)}]: ({_formula_tptp(f.body)})"
    return str(f)


def _term_tptp(t: Term) -> str:
    if isinstance(t, Variable):
        return _var_tptp(t)
    if isinstance(t, Constant):
        return t.name
    if isinstance(t, Apply):
        args = ", ".join(_term_tptp(cast(Term, a)) for a in t._args)
        return f"{t.func}({args})"
    return str(t)


def _var_tptp(v: Variable) -> str:
    base = v.sym.replace("₀", "0").replace("₁", "1").replace("₂", "2")
    if v.sort != DEFAULT_SORT:
        return f"{base}:{v.sort.name}"
    return base
