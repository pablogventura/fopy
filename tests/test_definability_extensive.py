"""Extensive definability result and public API tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from fopy.finite import DefinabilityResult, check_definability, is_open_definable
from fopy.finite.definability import is_open_definable as _iso
from fopy.finite.hit import Counterexample
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
class TestDefinabilityResult:
    def test_fields_definable(self, minimal_model):
        target = minimal_model.targets["T0"]
        r = is_open_definable(minimal_model, target)
        assert isinstance(r.definable, bool)
        assert r.fragment == "open"

    def test_witness_on_counterexample(self):
        model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
        tname = next(iter(model.targets))
        r = is_open_definable(model, model.targets[tname])
        if not r.definable:
            assert r.counterexample is not None
            assert r.witness_tuples is not None
            assert len(r.witness_tuples) >= 1

    def test_formula_when_definable(self, minimal_model):
        target = minimal_model.targets["T0"]
        r = is_open_definable(minimal_model, target)
        if r.definable:
            assert r.formula is not None

    def test_check_alias(self, minimal_model):
        target = minimal_model.targets["T0"]
        assert check_definability(minimal_model, target).definable == _iso(
            minimal_model, target
        ).definable


@pytest.mark.finite
class TestCounterexampleRepr:
    def test_repr(self):
        ce = Counterexample([[0, 1], [1, 0]])
        assert "Counterexample" in repr(ce)


@pytest.mark.finite
@pytest.mark.parametrize(
    "name,expected",
    [
        ("minimal.model", True),
        ("cadena4.model", True),
        ("retrombo_nodef.model", False),
        ("suma4.model", False),
    ],
)
def test_definability_expected_extended(name: str, expected: bool):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    assert is_open_definable(model, model.targets[tname]).definable is expected


@pytest.mark.finite
def test_definability_result_dataclass_defaults():
    r = DefinabilityResult(definable=False)
    assert r.formula is None
    assert r.counterexample is None
    assert r.witness_tuples is None
