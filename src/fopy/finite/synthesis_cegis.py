"""Counterexample-guided inductive synthesis of open defining formulas."""

from __future__ import annotations

from dataclasses import dataclass

from fopy.finite.model_checking import models
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula
from fopy.finite.relops import Relation
from fopy.finite.synthesis import synthesize_defining_formula


@dataclass
class CegisResult:
    """Outcome of a CEGIS synthesis loop.

    Attributes:
        formula: Witness open formula when synthesis succeeds.
        iterations: Number of refine rounds performed.
        success: Whether a defining formula was found.
    """

    formula: Formula | None
    iterations: int
    success: bool


def cegis_synthesize(
    model: Model,
    target: Relation,
    *,
    max_iters: int = 5,
    max_depth: int = 2,
) -> CegisResult:
    """Synthesize a quantifier-free defining formula via bounded CEGIS.

    Alternates candidate enumeration (up to *max_depth*) with model checking
    on the target extension. Each failed candidate is discarded; the loop
    stops after *max_iters* rounds or when a defining formula is found.

    Args:
        model: Finite algebra hosting the target relation.
        target: Relation whose extension must be matched.
        max_iters: Maximum refine iterations.
        max_depth: Maximum term grade for candidate formulas.

    Returns:
        :class:`CegisResult` with optional witness formula.
    """
    if max_iters < 1:
        raise ValueError("max_iters must be at least 1")
    goal = set(target.r)
    for iteration in range(1, max_iters + 1):
        depth = min(max_depth, iteration)
        result = synthesize_defining_formula(model, target, max_depth=depth)
        if result.formula is None:
            continue
        ext = result.formula.extension(model, target.arity)
        if ext == goal and models(model, result.formula):
            return CegisResult(formula=result.formula, iterations=iteration, success=True)
    fallback = synthesize_defining_formula(model, target, max_depth=max_depth)
    if fallback.formula is not None and fallback.formula.extension(model, target.arity) == goal:
        return CegisResult(formula=fallback.formula, iterations=max_iters, success=True)
    return CegisResult(formula=None, iterations=max_iters, success=False)
