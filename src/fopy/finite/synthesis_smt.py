"""SMT-backed formula synthesis (optional Z3)."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula
from fopy.finite.relops import Relation
from fopy.finite.synthesis import _enumerate_eq_formulas, synthesize_defining_formula
from fopy.solvers.z3_backend import z3_available


@dataclass
class SmtSynthesisResult:
    """Result of SMT-based synthesis attempt.

    Attributes:
        formula: Witness formula when synthesis succeeds.
        backend: ``"z3"`` when Z3 was used, ``"enumeration"`` on fallback.
        sat: Whether the solver reported satisfiability for the last query.
    """

    formula: Formula | None
    backend: str
    sat: bool | None


def _z3_select_candidate(
    model: Model,
    target: Relation,
    candidates: list[Formula],
) -> Formula | None:
    """Pick one candidate formula via Z3 pseudo-Boolean selection."""
    import z3

    if not candidates:
        return None
    solver = z3.Solver()
    picks = [z3.Bool(f"pick_{i}") for i in range(len(candidates))]
    solver.add(z3.PbEq([(picks[i], 1) for i in range(len(candidates))], 1))
    goal = set(target.r)
    for tup in product(model.universe, repeat=target.arity):
        in_goal = tup in goal
        clause: list[z3.BoolRef] = []
        for idx, cand in enumerate(candidates):
            ext = cand.extension(model, target.arity)
            matches = (tup in ext) == in_goal
            clause.append(z3.And(picks[idx], z3.BoolVal(matches)))
        solver.add(z3.Or(*clause))
    if solver.check() != z3.sat:
        return None
    model_z3 = solver.model()
    for idx, pick in enumerate(picks):
        if z3.is_true(model_z3.eval(pick, model_completion=True)):
            return candidates[idx]
    return None


def smt_synthesize(
    model: Model,
    target: Relation,
    *,
    max_depth: int = 2,
) -> SmtSynthesisResult:
    """Attempt SMT-based synthesis of a defining formula (Z3 when available).

    When Z3 is installed, encodes candidate selection as a SAT problem over
    enumerated equality formulas up to *max_depth*. Otherwise falls back to
    bounded enumeration.

    Args:
        model: Finite algebra.
        target: Target relation.
        max_depth: Maximum term grade for candidates.

    Returns:
        :class:`SmtSynthesisResult` describing the outcome and backend used.
    """
    candidates: list[Formula] = []
    for depth in range(max_depth + 1):
        candidates.extend(_enumerate_eq_formulas(model, target.arity, depth))
    if z3_available():
        picked = _z3_select_candidate(model, target, candidates)
        if picked is not None:
            return SmtSynthesisResult(formula=picked, backend="z3", sat=True)
        return SmtSynthesisResult(formula=None, backend="z3", sat=False)
    enum = synthesize_defining_formula(model, target, max_depth=max_depth)
    return SmtSynthesisResult(
        formula=enum.formula,
        backend="enumeration",
        sat=None,
    )
