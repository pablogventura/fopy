"""String representation for FO expressions."""

from __future__ import annotations

from typing import cast

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


def to_python(expr: object) -> str:
    """Return a readable Python expression reconstructing *expr* via the fopy API.

    Suitable for notebooks and copy-paste round trips with :func:`fopy.parse.parse_formula`
    for the formula subset emitted here.
    """
    if isinstance(expr, Formula):
        return _formula_python(expr)
    if isinstance(expr, Term):
        return _term_python(expr)
    return repr(expr)


def _term_python(t: Term | Variable) -> str:
    if isinstance(t, Variable):
        if t.sort.name != "U":
            return f'fo.Variable("{t.sym}", fo.Sort("{t.sort.name}"))'
        return f'fo.symbols("{t.sym}")'
    if isinstance(t, Constant):
        return f'fo.Constant("{t.name}")'
    if isinstance(t, Apply):
        args = ", ".join(_term_python(cast(Term, a)) for a in t._args)
        return f"fo.Apply(fo.FuncSymbol({t.func!r}, {len(t._args)}), ({args},))"
    return repr(t)


def _formula_python(f: Formula) -> str:
    if isinstance(f, TrueF):
        return "fo.true_formula()"
    if isinstance(f, FalseF):
        return "fo.false_formula()"
    if isinstance(f, Atom):
        args = ", ".join(_term_python(a) for a in f._args)
        return f"fo.Atom({f.rel!r}, ({args},))"
    if isinstance(f, Eq):
        return f"fo.eq({_term_python(f.left)}, {_term_python(f.right)})"
    if isinstance(f, Not):
        return f"fo.neg({_formula_python(f.arg)})"
    if isinstance(f, And):
        parts = [_formula_python(c) for c in sorted(f.children, key=repr)]
        if len(parts) == 1:
            return parts[0]
        joined = ", ".join(parts)
        return f"fo.and_formula({joined})"
    if isinstance(f, Or):
        parts = [_formula_python(c) for c in sorted(f.children, key=repr)]
        if len(parts) == 1:
            return parts[0]
        joined = ", ".join(parts)
        return f"fo.or_formula({joined})"
    if isinstance(f, ForAll):
        var = _term_python(f.var)
        return f"fo.forall({var}, {_formula_python(f.body)})"
    if isinstance(f, Exists):
        var = _term_python(f.var)
        return f"fo.exists({var}, {_formula_python(f.body)})"
    return repr(f)


def _term_str(t: Term) -> str:
    if isinstance(t, Variable):
        return t.sym
    if isinstance(t, Constant):
        return t.name
    if isinstance(t, Apply):
        args = ", ".join(_term_str(cast(Term, a)) for a in t._args)
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
