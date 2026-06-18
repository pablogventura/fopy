"""High-level formula synthesis search API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fopy.finite.definability import check_definability, is_open_definable
from fopy.finite.explain import normalize_fragment
from fopy.finite.models import Model
from fopy.finite.relops import Relation
from fopy.finite.synthesis import (
    SynthesisResult,
    formula_max_term_depth,
    synthesize_defining_formula,
)

Strategy = Literal["enumerate", "cegis", "smt"]
_QF_ALIASES = frozenset({"qf", "open", "quantifier-free"})


@dataclass
class FormulaSearch:
    """Search for a defining open formula over a finite algebra.

    Wraps enumeration-based synthesis with optional minimization by term depth.
    Strategies ``cegis`` and ``smt`` apply to the quantifier-free fragment;
    other fragments return the witness from :func:`~fopy.finite.definability.check_definability`.

    Attributes:
        model: Finite algebra whose operations may define the target.
        target: Relation whose extension must be matched.
        fragment: Logic fragment label (``qf``, ``pp``, ``ep``, ``horn``, ``fo``, …).
        max_depth: Maximum term grade during enumeration.
        minimize: When ``True``, prefer lower complexity among QF witnesses.
        strategy: ``"enumerate"``, ``"cegis"``, or ``"smt"`` (QF only).
    """

    model: Model
    target: Relation
    fragment: str = "qf"
    max_depth: int = 3
    minimize: bool = True
    strategy: Strategy = "enumerate"

    def run(self) -> SynthesisResult:
        """Execute the search and return the best formula found.

        Returns:
            :class:`~fopy.finite.synthesis.SynthesisResult` with witness formula
            when definable.

        Raises:
            NotImplementedError: If *fragment* is not supported.
        """
        norm = normalize_fragment(self.fragment)
        if self.strategy in {"cegis", "smt"} and norm not in _QF_ALIASES:
            raise NotImplementedError(
                f"Strategy {self.strategy!r} applies only to quantifier-free fragments."
            )
        if norm not in _QF_ALIASES:
            result = check_definability(self.model, self.target, fragment=norm)
            if not result.definable or result.formula is None:
                return SynthesisResult(
                    formula=None, minimal=False, min_term_depth=None, exhausted=True
                )
            depth = formula_max_term_depth(result.formula)
            return SynthesisResult(
                formula=result.formula,
                minimal=False,
                min_term_depth=depth,
                exhausted=True,
            )
        if self.strategy == "cegis":
            from fopy.finite.synthesis_cegis import cegis_synthesize

            cegis = cegis_synthesize(self.model, self.target, max_depth=self.max_depth)
            if cegis.success and cegis.formula is not None:
                depth = formula_max_term_depth(cegis.formula)
                return SynthesisResult(
                    formula=cegis.formula,
                    minimal=False,
                    min_term_depth=depth,
                    exhausted=cegis.iterations >= 1,
                )
            return SynthesisResult(formula=None, minimal=False, min_term_depth=None, exhausted=True)
        if self.strategy == "smt":
            from fopy.finite.synthesis_smt import smt_synthesize

            smt = smt_synthesize(self.model, self.target, max_depth=self.max_depth)
            if smt.formula is not None:
                depth = formula_max_term_depth(smt.formula)
                enum = synthesize_defining_formula(
                    self.model, self.target, max_depth=self.max_depth
                )
                return SynthesisResult(
                    formula=smt.formula,
                    minimal=enum.minimal and enum.formula == smt.formula,
                    min_term_depth=depth,
                    exhausted=enum.exhausted,
                )
            return SynthesisResult(formula=None, minimal=False, min_term_depth=None, exhausted=True)
        check = is_open_definable(self.model, self.target)
        if not check.definable:
            return SynthesisResult(formula=None, minimal=False, min_term_depth=None, exhausted=True)
        if self.minimize:
            return synthesize_defining_formula(self.model, self.target, max_depth=self.max_depth)
        if check.formula is None:
            return SynthesisResult(formula=None, minimal=False, min_term_depth=None, exhausted=True)
        depth = formula_max_term_depth(check.formula)
        return SynthesisResult(
            formula=check.formula, minimal=False, min_term_depth=depth, exhausted=False
        )
