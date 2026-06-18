"""Synthesis of defining formulas."""

from __future__ import annotations

import pytest

from fopy.finite import is_open_definable, synthesize_defining_formula
from fopy.parse import parse_model

MODELS = __import__("pathlib").Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
def test_synthesize_minimal_model(minimal_model):
    target = minimal_model.targets["T0"]
    syn = synthesize_defining_formula(minimal_model, target, max_depth=2)
    check = is_open_definable(minimal_model, target)
    if check.definable:
        assert syn.formula is not None
        ext = syn.formula.extension(minimal_model, target.arity)
        assert ext == set(target.r)


@pytest.mark.finite
def test_synthesize_not_definable():
    model = parse_model(MODELS / "algebra.model", preprocess=True)
    tname = next(s for s in model.relations if s.startswith("T"))
    syn = synthesize_defining_formula(model, model.relations[tname], max_depth=1)
    assert syn.formula is None or not is_open_definable(model, model.relations[tname]).definable
