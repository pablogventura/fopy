"""FO formula parser."""

from __future__ import annotations

import re
from typing import cast

from fopy.formulas import Atom, Exists, ForAll, Formula
from fopy.simplify import and_formula, neg, or_formula
from fopy.simplify import eq as mk_eq
from fopy.sorts import Sort
from fopy.symbols import Variable
from fopy.terms import Apply, Constant, Term

_UNICODE = str.maketrans(
    {
        "∀": "forall ",
        "∃": "exists ",
        "¬": "~",
        "∧": "&",
        "∨": "|",
        "→": "->",
        "←": "<-",
        "↔": "<->",
    }
)


def _normalize(s: str) -> str:
    s = s.translate(_UNICODE)
    s = re.sub(r"\bfor\s+all\b", "forall", s, flags=re.I)
    s = re.sub(r"\bexists\b", "exists", s, flags=re.I)
    return s.strip()


def _find_top_level(s: str, ch: str) -> int | None:
    depth = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
            i += 1
            continue
        if c == ")":
            depth -= 1
            i += 1
            continue
        if depth == 0 and s.startswith(ch, i):
            return i
        i += 1
    return None


def _parse_variable_name(s: str) -> Variable:
    """Parse ``name`` or ``name:Sort`` variable declarations."""
    s = s.strip()
    if ":" in s:
        name, sort_name = s.split(":", 1)
        return Variable(name.strip(), Sort(sort_name.strip()))
    return Variable(s)


def parse_term(
    s: str,
    funcs: dict[str, int] | None = None,
    vars_map: dict[str, Variable] | None = None,
) -> Term:
    """Parse a first-order term string.

    Args:
        s: Source text for the term.
        funcs: Optional map of function symbols to arities.
        vars_map: Mutable map reused to assign stable :class:`~fopy.symbols.Variable`
            objects to free names.

    Returns:
        Parsed :class:`~fopy.terms.Term`.
    """
    s = s.strip()
    funcs = funcs or {}
    vars_map = vars_map or {}
    m = re.match(r"(\w+)\((.*)\)$", s)
    if m:
        name, inner = m.group(1), m.group(2)
        arity = funcs.get(name, inner.count(",") + 1 if inner else 0)
        if arity == 0:
            return Constant(name)
        parts = _split_args(inner)
        args = tuple(parse_term(p, funcs, vars_map) for p in parts)
        return Apply(name, args)
    if s not in vars_map:
        vars_map[s] = _parse_variable_name(s)
    return cast(Term, vars_map[s])


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


def parse_formula(
    s: str,
    funcs: dict[str, int] | None = None,
    rels: dict[str, int] | None = None,
) -> Formula:
    """Parse a first-order formula string.

    Supports ASCII and Unicode connectives/quantifiers (``∀``, ``∃``, ``∧``, …).

    Args:
        s: Source text for the formula.
        funcs: Optional map of function symbols to arities.
        rels: Optional map of relation symbols to arities.

    Returns:
        Parsed :class:`~fopy.formulas.Formula`.

    Raises:
        ValueError: If *s* is not a valid formula.

    Examples:
        >>> from fopy.parse import parse_formula
        >>> parse_formula("forall x exists y R(x,y)", rels={"R": 2})
        ∀x ∃y R(x, y)
    """
    s = _normalize(s)
    funcs = funcs or {}
    rels = rels or {}
    vars_map: dict[str, Variable] = {}

    if s.startswith("forall "):
        rest = s[7:].strip()
        sp = rest.split(None, 1)
        var = _parse_variable_name(sp[0])
        return ForAll(var, parse_formula(sp[1], funcs, rels))
    if s.startswith("exists "):
        rest = s[7:].strip()
        sp = rest.split(None, 1)
        var = _parse_variable_name(sp[0])
        return Exists(var, parse_formula(sp[1], funcs, rels))

    idx = _find_top_level(s, "<->")
    if idx is not None:
        left = parse_formula(s[:idx], funcs, rels)
        right = parse_formula(s[idx + 3 :], funcs, rels)
        return and_formula(left >> right, right >> left)

    idx = _find_top_level(s, "->")
    if idx is not None:
        return parse_formula(s[:idx], funcs, rels) >> parse_formula(s[idx + 2 :], funcs, rels)

    idx = _find_top_level(s, "<-")
    if idx is not None:
        return parse_formula(s[idx + 2 :], funcs, rels) >> parse_formula(s[:idx], funcs, rels)

    idx = _find_top_level(s, "|")
    if idx is not None:
        return or_formula(
            parse_formula(s[:idx], funcs, rels),
            parse_formula(s[idx + 1 :], funcs, rels),
        )
    idx = _find_top_level(s, "&")
    if idx is not None:
        return and_formula(
            parse_formula(s[:idx], funcs, rels),
            parse_formula(s[idx + 1 :], funcs, rels),
        )
    if s.startswith(("~", "-")):
        return neg(parse_formula(s[1:], funcs, rels))
    if s.startswith("(") and s.endswith(")"):
        return parse_formula(s[1:-1], funcs, rels)

    m = re.match(r"(\w+)\((.*)\)$", s)
    if m and m.group(1) in rels:
        name = m.group(1)
        parts = _split_args(m.group(2))
        args = tuple(parse_term(p, funcs, vars_map) for p in parts)
        return Atom(name, args)

    if "=" in s and "(" not in s.split("=")[0]:
        lhs_str, rhs_str = s.split("=", 1)
        return mk_eq(
            parse_term(lhs_str.strip(), funcs, vars_map),
            parse_term(rhs_str.strip(), funcs, vars_map),
        )

    raise ValueError(f"Cannot parse formula: {s}")
