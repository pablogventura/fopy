"""Tests for explain_definability and ExplainReport."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers_finite import assert_explain_agrees_with_check, assert_formula_defines

from fopy.bridge import from_finite_model
from fopy.finite import (
    ExplainReport,
    explain_definability,
    normalize_fragment,
    verify_certificate,
)
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
def test_explain_minimal_definable(minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    assert report.definable is True
    assert report.fragment == "qf"
    assert report.formula is not None
    assert "definable" in report.pretty().lower()
    assert_formula_defines(minimal_model, report.formula, minimal_model.targets["T0"])
    cert = report.certificate()
    assert verify_certificate(cert, minimal_model, "T0")
    assert_explain_agrees_with_check(minimal_model, minimal_model.targets["T0"])


@pytest.mark.finite
def test_explain_not_definable():
    model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
    tname = next(iter(model.targets))
    report = explain_definability(model, tname, max_synth_depth=0)
    assert report.definable is False
    assert report.obstruction is not None
    assert "not definable" in report.pretty().lower()
    assert len(report.witness_tuples) >= 1
    cert = report.certificate()
    assert verify_certificate(cert, model, tname)


@pytest.mark.finite
def test_explain_structure_bridge(minimal_model):
    struct = from_finite_model(minimal_model)
    report = explain_definability(struct, "T0", max_synth_depth=0)
    assert isinstance(report, ExplainReport)


@pytest.mark.finite
def test_fragment_aliases():
    assert normalize_fragment("open") == "qf"
    assert normalize_fragment("quantifier-free") == "qf"
    assert normalize_fragment("pp") == "pp"
    assert normalize_fragment("fo") == "fo"


@pytest.mark.finite
def test_explain_golden_hybrid(minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    text = report.pretty()
    assert "T0" in text
    assert report.proof_sketch()
    if report.definable and report.formula:
        assert_formula_defines(minimal_model, report.formula, minimal_model.targets["T0"])
