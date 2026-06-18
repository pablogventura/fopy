"""Model checking API on finite models."""

from __future__ import annotations

import pytest

from fopy.finite import counterexample, models, satisfying_assignments
from fopy.finite.open_formulas import Term, Variable, eq
from fopy.finite.open_parse import parse_open_formula


@pytest.mark.finite
def test_models_universal_identity(minimal_model):
    x = Variable.new("x")
    y = Variable.new("y")
    f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
    # f(x,y)=x is not universal on minimal model
    assert models(minimal_model, f) is False


@pytest.mark.finite
def test_counterexample_found(minimal_model):
    x = Variable.new("x")
    y = Variable.new("y")
    f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, minimal_model.operations)
    ce = counterexample(minimal_model, f)
    assert ce is not None


@pytest.mark.finite
def test_satisfying_assignments(minimal_model):
    x = Variable.new("x")
    t = eq(Term.from_variable(x), Term.from_variable(x))
    assigns = satisfying_assignments(minimal_model, t)
    assert len(assigns) == len(minimal_model.universe)


@pytest.mark.finite
def test_model_methods(minimal_model):
    x = Variable.new("x")
    t = eq(Term.from_variable(x), Term.from_variable(x))
    assert minimal_model.models(t) is True
    assert minimal_model.satisfying_assignments(t)
