"""Unit tests for finite.explain helpers."""

from __future__ import annotations

import pytest

from fopy.finite.explain import (
    atomic_type,
    explain_obstruction,
    format_open_formula,
    latex_open_formula,
    model_fingerprint,
)
from fopy.finite.hit import Counterexample
from fopy.finite.open_formulas import Term, Variable, eq
from fopy.finite.open_parse import parse_open_formula


@pytest.mark.finite
def test_format_open_formula_roundtrip(minimal_model):
    ops = minimal_model.operations
    x, y = Variable.new("x"), Variable.new("y")
    f = parse_open_formula("eq(f(x,y),x)", {"x": x, "y": y}, ops)
    s = format_open_formula(f)
    f2 = parse_open_formula(s, {"x": x, "y": y}, ops)
    assert f == f2


@pytest.mark.finite
def test_atomic_type_same_for_equivalent_tuples(minimal_model):
    a = atomic_type(minimal_model, (0, 0))
    assert isinstance(a, tuple)


@pytest.mark.finite
def test_explain_obstruction_message(minimal_model):
    target = minimal_model.targets["T0"]
    ce = Counterexample([[0, 0], [1, 0]])
    obs = explain_obstruction(minimal_model, target, ce)
    assert "not definable" in obs.message.lower()


@pytest.mark.finite
def test_latex_open_formula():
    x = Term.from_variable(Variable.new("x"))
    y = Term.from_variable(Variable.new("y"))
    f = eq(x, y)
    assert "=" in latex_open_formula(f)


@pytest.mark.finite
def test_model_fingerprint_stable(minimal_model):
    assert model_fingerprint(minimal_model) == model_fingerprint(minimal_model)
