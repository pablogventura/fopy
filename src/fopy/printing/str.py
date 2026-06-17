"""String representation for FO expressions."""

from __future__ import annotations

from fopy.formulas import And, Atom, Eq, Exists, FalseF, ForAll, Formula, Not, Or, TrueF
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def sstr(expr: object) -> str:
    """Return a plain string for a term or formula."""
    if isinstance(expr, Formula):
        return _formula_str(expr)
    if isinstance(expr, Term):
        return _term_str(expr)
    return str(expr)


def _term_str(t: Term) -> str:
    if isinstance(t, Variable):
        return t.sym
    if isinstance(t, Constant):
        return t.name
    if isinstance(t, Apply):
        args = ", ".join(_term_str(a) for a in t._args)
        return f"{t.func}({args})"
    return repr(t)


def _formula_str(f: Formula) -> str:
    if isinstance(f, TrueF):
        return "true"
    if isinstance(f, FalseF):
        return "false"
    if isinstance(f, Atom):
        args = ", ".join(_term_str(a) for a in f._args)
        return f"{f.rel}({args})"
    if isinstance(f, Eq):
        return f"{_term_str(f.left)} = {_term_str(f.right)}"
    if isinstance(f, Not):
        return f"~{_formula_str(f.arg)}"
    if isinstance(f, And):
        parts = " & ".join(_formula_str(c) for c in sorted(f.children, key=repr))
        return f"({parts})" if len(f.children) > 1 else parts
    if isinstance(f, Or):
        parts = " | ".join(_formula_str(c) for c in sorted(f.children, key=repr))
        return f"({parts})" if len(f.children) > 1 else parts
    if isinstance(f, ForAll):
        return f"forall {f.var.sym} {_formula_str(f.body)}"
    if isinstance(f, Exists):
        return f"exists {f.var.sym} {_formula_str(f.body)}"
    return repr(f)
