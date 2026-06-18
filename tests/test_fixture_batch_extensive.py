"""Fast batch checks on a tiny curated model set (CI finite job)."""

from __future__ import annotations

import pytest
from helpers_models import CORE_CERT_MODELS, CORE_DEFINABILITY, MODELS_DIR

from fopy.finite import explain_definability, is_open_definable, verify_certificate
from fopy.parse import parse_model

MODELS = MODELS_DIR


@pytest.mark.finite
@pytest.mark.parametrize("name", CORE_DEFINABILITY)
def test_definability_matches_explain_fast(name: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    target = model.targets[tname]
    check = is_open_definable(model, target)
    report = explain_definability(model, tname, max_synth_depth=0)
    assert report.definable == check.definable


@pytest.mark.finite
@pytest.mark.parametrize("name", CORE_CERT_MODELS)
def test_explain_certificate_fast(name: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    report = explain_definability(model, tname, max_synth_depth=0)
    cert = report.certificate_with_model(model)
    assert verify_certificate(cert, model, tname)
