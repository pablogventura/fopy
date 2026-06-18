"""Open-term formula parser for .model files."""

from __future__ import annotations

from fopy.finite.open_formulas import (
    Formula,
    OpSym,
    Term,
    Variable,
    and_formula,
    eq,
    neg,
    or_formula,
)
from fopy.finite.relops import Operation


def _find_top_level(s: str, ch: str) -> int | None:
    depth = 0
    for i, c in enumerate(s):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == ch and depth == 0:
            return i
    return None


def _split_args(s: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for i, c in enumerate(s):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(s[start:i].strip())
            start = i + 1
    parts.append(s[start:].strip())
    return [p for p in parts if p]


def parse_term(
    s: str,
    vars_map: dict[str, Variable],
    operations: dict[str, Operation],
) -> Term:
    """Parse an open term string using *vars_map* and *operations*.

    Args:
        s: Source text (variable name or ``op(arg1, ...)``).
        vars_map: Maps variable symbols to :class:`~fopy.finite.open_formulas.Variable`.
        operations: Available operations (used for arity validation context).

    Returns:
        Parsed :class:`~fopy.finite.open_formulas.Term`.

    Raises:
        ValueError: If *s* is not a known variable or operation application.
    """
    s = s.strip()
    if s in vars_map:
        return Term.from_variable(vars_map[s])
    if "(" in s:
        lp = s.index("(")
        name = s[:lp]
        inner = s[lp + 1 : -1]
        args = [parse_term(a, vars_map, operations) for a in _split_args(inner)]
        return Term.op_term(OpSym.new(name, len(args)), args)
    raise ValueError(f"Unknown term: {s}")


def parse_open_formula(
    s: str,
    vars_map: dict[str, Variable],
    operations: dict[str, Operation],
) -> Formula:
    """Parse an open quantifier-free formula over term equality.

    Supports ``&``, ``|``, unary ``-`` (negation), ``true``, ``false``, and
    ``eq(t1, t2)`` atoms.

    Args:
        s: Source text.
        vars_map: Variable symbol table.
        operations: Operation signature for term parsing.

    Returns:
        Parsed :class:`~fopy.finite.open_formulas.Formula`.

    Raises:
        ValueError: If *s* cannot be parsed.
    """
    s = s.strip()
    idx = _find_top_level(s, "|")
    if idx is not None:
        return or_formula(
            parse_open_formula(s[:idx], vars_map, operations),
            parse_open_formula(s[idx + 1 :], vars_map, operations),
        )
    idx = _find_top_level(s, "&")
    if idx is not None:
        return and_formula(
            parse_open_formula(s[:idx], vars_map, operations),
            parse_open_formula(s[idx + 1 :], vars_map, operations),
        )
    if s.startswith("-"):
        return neg(parse_open_formula(s[1:], vars_map, operations))
    if s == "true":
        from fopy.finite.open_formulas import true_formula

        return true_formula(None)
    if s == "false":
        from fopy.finite.open_formulas import false_formula

        return false_formula(None)
    if s.startswith("eq("):
        inner = s[3:-1]
        comma = _find_top_level(inner, ",") or inner.index(",")
        t1 = parse_term(inner[:comma].strip(), vars_map, operations)
        t2 = parse_term(inner[comma + 1 :].strip(), vars_map, operations)
        return eq(t1, t2)
    raise ValueError(f"Cannot parse: {s}")
