"""High-level formula synthesis search API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fopy.finite.definability import is_open_definable
from fopy.finite.models import Model
from fopy.finite.relops import Relation
from fopy.finite.synthesis import SynthesisResult, synthesize_defining_formula

Strategy = Literal["enumerate", "cegis", "smt"]


@dataclass
class FormulaSearch:
    """Search for a defining open formula over a finite algebra.

    Wraps enumeration-based synthesis with optional minimization by term depth.
    Strategies ``cegis`` and ``smt`` use bounded refinement loops when available.

    Attributes:
        model: Finite algebra whose operations may define the target.
        target: Relation whose extension must be matched.
        fragment: Logic fragment label (currently only ``"qf"``).
        max_depth: Maximum term grade during enumeration.
        minimize: When ``True``, prefer lower term depth among witnesses.
        strategy: ``"enumerate"``, ``"cegis"``, or ``"smt"``.
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
            NotImplementedError: If *fragment* is not ``"qf"`` / ``"open"``.
        """
        key = self.fragment.strip().lower()
        if key not in {"qf", "open", "quantifier-free"}:
            raise NotImplementedError(f"Fragment {self.fragment!r} is not supported.")
        if self.strategy == "cegis":
            from fopy.finite.synthesis_cegis import cegis_synthesize

            cegis = cegis_synthesize(self.model, self.target, max_depth=self.max_depth)
            if cegis.success and cegis.formula is not None:
                from fopy.finite.synthesis import formula_max_term_depth

                depth = formula_max_term_depth(cegis.formula)
                return SynthesisResult(
                    formula=cegis.formula,
                    minimal=False,
                    min_term_depth=depth,
                    exhausted=cegis.iterations >= 1,
                )
            return SynthesisResult(
                formula=None, minimal=False, min_term_depth=None, exhausted=True
            )
        if self.strategy == "smt":
            from fopy.finite.synthesis_smt import smt_synthesize

            smt = smt_synthesize(self.model, self.target, max_depth=self.max_depth)
            if smt.formula is not None:
                from fopy.finite.synthesis import formula_max_term_depth

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
            return SynthesisResult(
                formula=None, minimal=False, min_term_depth=None, exhausted=True
            )
        check = is_open_definable(self.model, self.target)
        if not check.definable:
            return SynthesisResult(
                formula=None, minimal=False, min_term_depth=None, exhausted=True
            )
        if self.minimize:
            return synthesize_defining_formula(
                self.model, self.target, max_depth=self.max_depth
            )
        if check.formula is None:
            return SynthesisResult(
                formula=None, minimal=False, min_term_depth=None, exhausted=True
            )
        from fopy.finite.synthesis import formula_max_term_depth

        depth = formula_max_term_depth(check.formula)
        return SynthesisResult(
            formula=check.formula, minimal=False, min_term_depth=depth, exhausted=False
        )
