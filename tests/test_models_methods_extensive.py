"""Extensive tests for Model convenience methods (phase 2)."""

from __future__ import annotations

import pytest

from fopy.finite.open_formulas import Term, Variable, eq, false_formula, true_formula
from fopy.finite.synthesis import synthesize_defining_formula


@pytest.mark.finite
class TestModelMethods:
    def test_models_false(self, minimal_model):
        x = Variable.new("x")
        f = false_formula({x})
        assert not minimal_model.models(f)

    def test_models_true_unary(self, minimal_model):
        x = Variable.new("x")
        f = true_formula({x})
        assert minimal_model.models(f)

    def test_counterexample_false(self, minimal_model):
        x = Variable.new("x")
        f = false_formula({x})
        assert minimal_model.counterexample(f) is not None

    def test_satisfying_assignments(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assigns = minimal_model.satisfying_assignments(f)
        assert len(assigns) == len(minimal_model.universe)

    def test_term_functions(self, minimal_model):
        funcs = minimal_model.term_functions(max_depth=1)
        assert isinstance(funcs, dict)

    def test_subalgebra_generated_by(self, minimal_model):
        sub = minimal_model.subalgebra_generated_by([0])
        assert 0 in sub

    def test_show_tables_nonempty(self, minimal_model):
        text = minimal_model.show_tables()
        assert "universe" in text
        assert "T0" in text or "operation" in text


@pytest.mark.finite
class TestSynthesisHelpers:
    def test_synthesize_definable_target(self, minimal_model):
        target = minimal_model.targets["T0"]
        result = synthesize_defining_formula(minimal_model, target, max_depth=2)
        if result.formula is not None:
            assert result.formula.extension(minimal_model, target.arity) == set(target.r)

    def test_synthesis_depth_bounded(self, minimal_model):
        target = minimal_model.targets["T0"]
        result = synthesize_defining_formula(minimal_model, target, max_depth=1)
        if result.min_term_depth is not None:
            assert result.min_term_depth <= 1
