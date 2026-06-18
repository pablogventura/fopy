"""Post-hoc search for shorter equivalent open defining formulas."""

from __future__ import annotations

from dataclasses import dataclass

from fopy.finite.definability import is_open_definable
from fopy.finite.models import Model
from fopy.finite.open_formulas import (
    Formula,
    FormulaKind,
    OpSym,
    Term,
    Variable,
    eq,
)
from fopy.finite.relops import Relation


@dataclass
class SynthesisResult:
    """Result of searching for a shorter open defining formula.

    Attributes:
        formula: Best formula found, if any.
        minimal: Whether the formula is minimal among enumerated candidates.
        min_term_depth: Maximum term grade in the returned formula.
        exhausted: Whether enumeration fully explored the space up to *max_depth*.
    """

    formula: Formula | None
    minimal: bool
    min_term_depth: int | None
    exhausted: bool = False


def _target_extension(model: Model, target: Relation) -> set[tuple[int, ...]]:
    return set(target.r)


def _enumerate_eq_formulas(
    model: Model,
    arity: int,
    max_depth: int,
) -> list[Formula]:
    vars_ = [Variable.from_index(i) for i in range(arity)]
    terms: list[Term] = [Term.from_variable(v) for v in vars_]
    ops_by_arity: dict[int, list[str]] = {}
    for sym, op in model.operations.items():
        ops_by_arity.setdefault(op.arity, []).append(sym)
    for _depth in range(1, max_depth + 1):
        for ar, syms in sorted(ops_by_arity.items()):
            if ar == 0:
                for sym in syms:
                    terms.append(Term.op_term(OpSym.new(sym, 0), []))
            else:
                for sym in syms:
                    for combo in _term_combos(terms, ar):
                        terms.append(Term.op_term(OpSym.new(sym, ar), list(combo)))
    formulas: list[Formula] = []
    seen: set[int] = set()
    for i, t1 in enumerate(terms):
        for t2 in terms[i:]:
            f = eq(t1, t2)
            h = hash(f)
            if h not in seen:
                seen.add(h)
                formulas.append(f)
    return formulas


def _term_combos(terms: list[Term], arity: int) -> list[tuple[Term, ...]]:
    if arity == 0:
        return [()]
    result: list[tuple[Term, ...]] = [()]
    for _ in range(arity):
        result = [r + (t,) for r in result for t in terms]
    return result


def synthesize_defining_formula(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 3,
) -> SynthesisResult:
    """Find a quantifier-free defining formula, preferring lower term depth.

    Enumerates equality formulas up to *max_depth*; falls back to HIT via
    :func:`~fopy.finite.definability.is_open_definable` when enumeration fails.

    Args:
        model: Structure whose operations may define *target*.
        target: Relation whose extension must be matched.
        max_depth: Maximum term grade to try during enumeration.

    Returns:
        :class:`SynthesisResult` with the best formula found, if any.
    """
    goal = _target_extension(model, target)
    best: Formula | None = None
    best_score = (max_depth + 1, max_depth + 1)
    seen_extensions: set[frozenset[tuple[int, ...]]] = set()
    for depth in range(max_depth + 1):
        for f in _enumerate_eq_formulas(model, target.arity, depth):
            ext = f.extension(model, target.arity)
            ext_key = frozenset(ext)
            if ext_key in seen_extensions:
                continue
            seen_extensions.add(ext_key)
            if ext == goal:
                score = formula_complexity(f)
                if score < best_score:
                    best = f
                    best_score = score
        if best is not None:
            return SynthesisResult(
                formula=best,
                minimal=True,
                min_term_depth=best_score[0],
                exhausted=True,
            )
    hit = is_open_definable(model, target)
    if hit.definable and hit.formula is not None:
        depth = _formula_max_term_depth(hit.formula)
        return SynthesisResult(
            formula=hit.formula, minimal=False, min_term_depth=depth, exhausted=True
        )
    return SynthesisResult(formula=None, minimal=False, min_term_depth=None, exhausted=True)


def formula_max_term_depth(formula: Formula) -> int:
    """Return the maximum term grade appearing in an open formula."""
    return _formula_max_term_depth(formula)


def formula_complexity(formula: Formula) -> tuple[int, int]:
    """Return ``(max_term_depth, ast_node_count)`` for ranking witnesses."""
    return (_formula_max_term_depth(formula), _formula_ast_size(formula))


def _formula_ast_size(formula: Formula) -> int:
    match formula.kind:
        case FormulaKind.EQ:
            return 1
        case FormulaKind.NEG:
            assert formula.inner is not None
            return 1 + _formula_ast_size(formula.inner)
        case FormulaKind.AND | FormulaKind.OR:
            return 1 + sum(_formula_ast_size(p) for p in formula.parts)
        case _:
            return 1


def _formula_max_term_depth(formula: Formula) -> int:
    match formula.kind:
        case FormulaKind.EQ:
            assert formula.t1 is not None
            assert formula.t2 is not None
            return max(formula.t1.grade(), formula.t2.grade())
        case FormulaKind.NEG:
            assert formula.inner is not None
            return _formula_max_term_depth(formula.inner)
        case FormulaKind.AND | FormulaKind.OR:
            if not formula.parts:
                return 0
            return max(_formula_max_term_depth(p) for p in formula.parts)
        case _:
            return 0
