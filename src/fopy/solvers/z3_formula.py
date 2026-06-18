"""Convert symbolic FO formulas to Z3 expressions (optional)."""

from __future__ import annotations

from typing import Any, cast

from fopy.formulas import And, Atom, Eq, Exists, FalseF, ForAll, Formula, Not, Or, TrueF
from fopy.solvers.z3_backend import z3_available
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term


def formula_to_z3(phi: Formula) -> Any | None:
    """Translate a symbolic :class:`~fopy.formulas.Formula` into a Z3 expression.

    Requires the optional ``z3-solver`` package. Universe elements are
    modeled as uninterpreted integers; function and relation symbols become
    uninterpreted Z3 functions over ``Int``.

    Args:
        phi: First-order formula in the symbolic AST layer.

    Returns:
        Z3 ``BoolRef`` expression, or ``None`` when Z3 is not installed.
    """
    if not z3_available():
        return None
    import z3

    ctx: dict[str, Any] = {"z3": z3, "funs": {}, "rels": {}}
    return _formula_z3(phi, ctx)


def _formula_z3(f: Formula, ctx: dict[str, Any]) -> Any:
    z3 = ctx["z3"]
    if isinstance(f, TrueF):
        return z3.BoolVal(True)
    if isinstance(f, FalseF):
        return z3.BoolVal(False)
    if isinstance(f, Atom):
        rel = _rel_z3(f.rel, len(f._args), ctx)
        args = [_term_z3(t, ctx) for t in f._args]
        return rel(*args)
    if isinstance(f, Eq):
        return _term_z3(f.left, ctx) == _term_z3(f.right, ctx)
    if isinstance(f, Not):
        return z3.Not(_formula_z3(f.arg, ctx))
    if isinstance(f, And):
        return z3.And(*[_formula_z3(c, ctx) for c in f.children])
    if isinstance(f, Or):
        return z3.Or(*[_formula_z3(c, ctx) for c in f.children])
    if isinstance(f, ForAll):
        v = _var_z3(f.var, ctx)
        return z3.ForAll([v], _formula_z3(f.body, ctx))
    if isinstance(f, Exists):
        v = _var_z3(f.var, ctx)
        return z3.Exists([v], _formula_z3(f.body, ctx))
    return z3.BoolVal(True)


def _var_z3(v: Variable, ctx: dict[str, Any]) -> Any:
    z3 = ctx["z3"]
    key = f"v:{v.sym}"
    if key not in ctx["funs"]:
        ctx["funs"][key] = z3.Int(v.sym.replace("₀", "0").replace("₁", "1"))
    return ctx["funs"][key]


def _fun_z3(name: str, arity: int, ctx: dict[str, Any]) -> Any:
    z3 = ctx["z3"]
    key = f"f:{name}:{arity}"
    if key not in ctx["funs"]:
        sorts = [z3.IntSort()] * arity + [z3.IntSort()]
        ctx["funs"][key] = z3.Function(name, *sorts)
    return ctx["funs"][key]


def _rel_z3(name: str, arity: int, ctx: dict[str, Any]) -> Any:
    z3 = ctx["z3"]
    key = f"r:{name}:{arity}"
    if key not in ctx["rels"]:
        sorts = [z3.IntSort()] * arity + [z3.BoolSort()]
        ctx["rels"][key] = z3.Function(name, *sorts)
    return ctx["rels"][key]


def _term_z3(t: Term, ctx: dict[str, Any]) -> Any:
    z3 = ctx["z3"]
    if isinstance(t, Variable):
        return _var_z3(t, ctx)
    if isinstance(t, Constant):
        return z3.IntVal(t.name)
    if isinstance(t, Apply):
        fn = _fun_z3(t.func, len(t._args), ctx)
        return fn(*[cast(Term, a) for a in t._args])
    return z3.IntVal(0)
