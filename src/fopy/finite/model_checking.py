"""Model checking helpers for finite open formulas."""

from __future__ import annotations

from itertools import product

from fopy.finite.eval_cache import EvalCache, satisfy_cached
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, Variable


def models(
    model: Model,
    formula: Formula,
    *,
    cache: EvalCache | None = None,
) -> bool:
    """Return whether *formula* holds for all assignments over *model* universe.

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.
        cache: Optional shared :class:`~fopy.finite.eval_cache.EvalCache`.

    Returns:
        ``True`` iff every assignment satisfying implied variables makes
        *formula* true.
    """
    table = cache if cache is not None else EvalCache()
    vs = formula.implied_declaration()
    if not vs:
        return satisfy_cached(formula, model, {}, table)
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if not satisfy_cached(formula, model, vector, table):
            return False
    return True


def counterexample(
    model: Model,
    formula: Formula,
    *,
    cache: EvalCache | None = None,
) -> dict[Variable, int] | None:
    """Return one assignment falsifying *formula*, or ``None`` if none exists.

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.
        cache: Optional evaluation memo table.

    Returns:
        Variable assignment witnessing falsity, or ``None`` when the formula
        is valid on the model.
    """
    table = cache if cache is not None else EvalCache()
    vs = formula.implied_declaration()
    if not vs:
        return None if satisfy_cached(formula, model, {}, table) else {}
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if not satisfy_cached(formula, model, vector, table):
            return vector
    return None


def satisfying_assignments(
    model: Model,
    formula: Formula,
    *,
    cache: EvalCache | None = None,
) -> list[dict[Variable, int]]:
    """List all assignments making *formula* true (may be large).

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.
        cache: Optional evaluation memo table.

    Returns:
        Every variable assignment under which *formula* evaluates to true.
    """
    table = cache if cache is not None else EvalCache()
    vs = formula.implied_declaration()
    if not vs:
        return [{}] if satisfy_cached(formula, model, {}, table) else []
    result: list[dict[Variable, int]] = []
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if satisfy_cached(formula, model, vector, table):
            result.append(vector)
    return result
