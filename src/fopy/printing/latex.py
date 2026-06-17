"""LaTeX representation for FO expressions."""

from __future__ import annotations

from fopy.formulas import And, Atom, Eq, Exists, FalseF, ForAll, Formula, Not, Or, TrueF
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def latex(expr: object) -> str:
    """Return LaTeX for a term or formula."""
    if isinstance(expr, Formula):
        return _formula_latex(expr)
    if isinstance(expr, Term):
        return _term_latex(expr)
    return str(expr)


def _term_latex(t: Term) -> str:
    if isinstance(t, Variable):
        return _var_latex(t.sym)
    if isinstance(t, Constant):
        return f"\\mathrm{{{t.name}}}"
    if isinstance(t, Apply):
        args = ", ".join(_term_latex(a) for a in t._args)
        return f"\\mathrm{{{t.func}}}({args})"
    return repr(t)


def _var_latex(sym: str) -> str:
    if sym.startswith("x") and len(sym) > 1:
        sub = sym[1:]
        if sub and all(c in "₀₁₂₃₄₅₆₇₈₉₋" for c in sub):
            digits = sub.replace("₋", "-").translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
            return f"x_{{{digits}}}"
    return sym


def _formula_latex(f: Formula) -> str:
    if isinstance(f, TrueF):
        return "\\top"
    if isinstance(f, FalseF):
        return "\\bot"
    if isinstance(f, Atom):
        args = ", ".join(_term_latex(a) for a in f._args)
        return f"\\mathrm{{{f.rel}}}({args})"
    if isinstance(f, Eq):
        return f"{_term_latex(f.left)} = {_term_latex(f.right)}"
    if isinstance(f, Not):
        return f"\\neg {_formula_latex(f.arg)}"
    if isinstance(f, And):
        parts = " \\land ".join(_formula_latex(c) for c in sorted(f.children, key=repr))
        return f"\\left({parts}\\right)" if len(f.children) > 1 else parts
    if isinstance(f, Or):
        parts = " \\lor ".join(_formula_latex(c) for c in sorted(f.children, key=repr))
        return f"\\left({parts}\\right)" if len(f.children) > 1 else parts
    if isinstance(f, ForAll):
        return f"\\forall {_var_latex(f.var.sym)}\\, {_formula_latex(f.body)}"
    if isinstance(f, Exists):
        return f"\\exists {_var_latex(f.var.sym)}\\, {_formula_latex(f.body)}"
    return repr(f)
