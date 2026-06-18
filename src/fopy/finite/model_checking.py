"""Model checking helpers for finite open formulas."""

from __future__ import annotations

from itertools import product

from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, Variable


def models(model: Model, formula: Formula) -> bool:
    """Return whether *formula* holds for all assignments over *model* universe.

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.

    Returns:
        ``True`` iff every assignment satisfying implied variables makes
        *formula* true.
    """
    vs = formula.implied_declaration()
    if not vs:
        return formula.satisfy(model, {})
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if not formula.satisfy(model, vector):
            return False
    return True


def counterexample(model: Model, formula: Formula) -> dict[Variable, int] | None:
    """Return one assignment falsifying *formula*, or ``None`` if none exists.

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.

    Returns:
        Variable assignment witnessing falsity, or ``None`` when the formula
        is valid on the model.
    """
    vs = formula.implied_declaration()
    if not vs:
        return None if formula.satisfy(model, {}) else {}
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if not formula.satisfy(model, vector):
            return vector
    return None


def satisfying_assignments(
    model: Model,
    formula: Formula,
) -> list[dict[Variable, int]]:
    """List all assignments making *formula* true (may be large).

    Args:
        model: Finite structure for evaluation.
        formula: Open quantifier-free formula.

    Returns:
        Every variable assignment under which *formula* evaluates to true.
    """
    vs = formula.implied_declaration()
    if not vs:
        return [{}] if formula.satisfy(model, {}) else []
    result: list[dict[Variable, int]] = []
    for vals in product(model.universe, repeat=len(vs)):
        vector = dict(zip(vs, vals, strict=True))
        if formula.satisfy(model, vector):
            result.append(vector)
    return result
