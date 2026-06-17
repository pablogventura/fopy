"""High-level open definability interface."""

from __future__ import annotations

from dataclasses import dataclass

from fopy.finite.hit import Counterexample, HitConfig, is_open_def
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, false_formula
from fopy.finite.preprocessing import preprocesamiento2
from fopy.finite.relops import Relation


@dataclass
class DefinabilityResult:
    definable: bool
    formula: Formula | None = None
    counterexample: Counterexample | None = None


def is_open_definable(
    model: Model,
    target: Relation,
    config: HitConfig | None = None,
) -> DefinabilityResult:
    """Decide whether *target* is open-definable from the operations of *model*."""
    cfg = config or HitConfig()
    preprocessed = preprocesamiento2(target)
    combined = false_formula(None)
    for prep_target in preprocessed:
        result = is_open_def(model, [prep_target], cfg)
        if isinstance(result, Counterexample):
            return DefinabilityResult(definable=False, counterexample=result)
        post = prep_target.pattern.postprocessed_formula() if prep_target.pattern else result
        combined = combined.or_formula(result.and_formula(post))
    return DefinabilityResult(definable=True, formula=combined)
