"""Pretty-printed formulas."""

from __future__ import annotations

from fopy.formulas import Formula
from fopy.printing.str import sstr
from fopy.terms import Term


def pprint(expr: object) -> str:
    """Return a human-readable multi-line string when useful."""
    text = sstr(expr) if isinstance(expr, (Formula, Term)) else str(expr)
    if len(text) <= 72:
        return text
    if isinstance(expr, Formula):
        from fopy.formulas import And, Exists, ForAll, Not, Or

        if isinstance(expr, (ForAll, Exists)):
            quant = "forall" if isinstance(expr, ForAll) else "exists"
            var = expr.var.sym
            body = pprint(expr.body)
            return f"{quant} {var}\n  {body.replace(chr(10), chr(10) + '  ')}"
        if isinstance(expr, Not):
            return f"~(\n  {pprint(expr.arg)}\n)"
        if isinstance(expr, (And, Or)):
            sep = " & " if isinstance(expr, And) else " | "
            parts = [pprint(c) for c in sorted(expr.children, key=repr)]
            return sep.join(f"({p})" if "\n" in p else p for p in parts)
    return text
