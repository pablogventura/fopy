"""Extensive synthesis tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers_finite import assert_formula_defines

from fopy.finite import is_open_definable, synthesize_defining_formula
from fopy.finite.open_formulas import Term, Variable, eq
from fopy.finite.synthesis import SynthesisResult, _formula_max_term_depth
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
class TestSynthesizeDefiningFormula:
    def test_returns_synthesis_result(self, minimal_model):
        target = minimal_model.targets["T0"]
        result = synthesize_defining_formula(minimal_model, target, max_depth=2)
        assert isinstance(result, SynthesisResult)

    def test_definable_has_formula(self, minimal_model):
        target = minimal_model.targets["T0"]
        syn = synthesize_defining_formula(minimal_model, target, max_depth=2)
        check = is_open_definable(minimal_model, target)
        if check.definable:
            assert syn.formula is not None
            assert_formula_defines(minimal_model, syn.formula, target)

    def test_not_definable_may_return_none(self):
        model = parse_model(MODELS / "algebra.model", preprocess=True)
        tname = next(iter(model.targets))
        syn = synthesize_defining_formula(model, model.targets[tname], max_depth=1)
        if not is_open_definable(model, model.targets[tname]).definable:
            assert syn.formula is None or syn.minimal is False


@pytest.mark.finite
class TestFormulaMaxTermDepth:
    def test_eq_depth(self):
        x = Term.from_variable(Variable.new("x"))
        f = eq(x, x)
        assert _formula_max_term_depth(f) == 0

    def test_and_depth(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        from fopy.finite.open_formulas import and_formula

        f = and_formula(eq(x, x), eq(y, y))
        assert _formula_max_term_depth(f) == 0

    def test_false_kind(self):
        from fopy.finite.open_formulas import false_formula

        assert _formula_max_term_depth(false_formula(None)) == 0
