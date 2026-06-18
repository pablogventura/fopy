"""Extensive model checking tests."""

from __future__ import annotations

import pytest

from fopy.finite import counterexample, models, satisfying_assignments
from fopy.finite.open_formulas import Variable, eq, false_formula, true_formula
from fopy.finite.open_formulas import Term
from fopy.finite.open_parse import parse_open_formula


@pytest.mark.finite
class TestModelsFunction:
    def test_true_formula_all_arity(self, minimal_model):
        f = true_formula({Variable.from_index(0)})
        assert models(minimal_model, f)

    def test_false_formula(self, minimal_model):
        f = false_formula({Variable.from_index(0)})
        assert not models(minimal_model, f)

    def test_reflexivity_not_universal(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assert models(minimal_model, f)

    def test_fxy_eq_x_not_universal(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
        assert not models(minimal_model, f)


@pytest.mark.finite
class TestCounterexampleFunction:
    def test_none_when_valid(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assert counterexample(minimal_model, f) is None

    def test_found_when_invalid(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
        ce = counterexample(minimal_model, f)
        assert ce is not None
        assert not f.satisfy(minimal_model, ce)

    def test_false_without_vars(self, minimal_model):
        f = false_formula(None)
        ce = counterexample(minimal_model, f)
        assert ce == {}


@pytest.mark.finite
class TestSatisfyingAssignments:
    def test_x_eq_x_count(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assigns = satisfying_assignments(minimal_model, f)
        assert len(assigns) == len(minimal_model.universe)

    def test_false_empty(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(Variable.new("y")))
        assigns = satisfying_assignments(minimal_model, f)
        assert len(assigns) < len(minimal_model.universe) ** 2


@pytest.mark.finite
class TestModelMethods:
    def test_models_method(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assert minimal_model.models(f)

    def test_counterexample_method(self, minimal_model):
        f = false_formula({Variable.from_index(0)})
        assert minimal_model.counterexample(f) is not None

    def test_satisfying_assignments_method(self, minimal_model):
        x = Variable.new("x")
        f = eq(Term.from_variable(x), Term.from_variable(x))
        assert len(minimal_model.satisfying_assignments(f)) == 2

    def test_models_counterexample_duality(self, minimal_model):
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
        if not models(minimal_model, f):
            ce = counterexample(minimal_model, f)
            assert ce is not None
            assert not f.satisfy(minimal_model, ce)

    def test_show_tables_nonempty(self, minimal_model):
        text = minimal_model.show_tables()
        assert "universe" in text
        assert "f" in text or "operation" in text
