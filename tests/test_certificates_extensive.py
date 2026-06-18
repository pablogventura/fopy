"""Extensive certificate and TrustedKernel tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fopy.finite import (
    TrustedKernel,
    deserialize_certificate,
    explain_definability,
    serialize_certificate,
    verify_certificate,
)
from fopy.finite.explain import CERT_VERSION
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
class TestSerializeDeserialize:
    def test_roundtrip(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        blob = serialize_certificate(cert)
        loaded = deserialize_certificate(blob)
        assert loaded == cert

    def test_sorted_keys(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        blob = serialize_certificate(cert)
        parsed = json.loads(blob)
        keys = list(parsed.keys())
        assert keys == sorted(keys)


@pytest.mark.finite
class TestTrustedKernel:
    def test_verify_positive(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        assert TrustedKernel.verify(cert, minimal_model, "T0")

    def test_verify_from_json_string(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        blob = serialize_certificate(cert)
        assert TrustedKernel.verify(blob, minimal_model, "T0")

    def test_invalid_json_string(self, minimal_model):
        assert not TrustedKernel.verify("{not json", minimal_model, "T0")

    def test_wrong_version(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        cert["version"] = 0
        assert not TrustedKernel.verify(cert, minimal_model, "T0")

    def test_negative_model(self):
        model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
        tname = next(iter(model.targets))
        cert = explain_definability(model, tname, max_synth_depth=0).certificate()
        assert not cert["definable"]
        assert TrustedKernel.verify(cert, model, tname)

    def test_cert_version_constant(self):
        assert CERT_VERSION == 2


@pytest.mark.finite
@pytest.mark.parametrize(
    "name",
    ["minimal.model", "retrombo_nodef.model"],
)
def test_certificate_verify_parametric(name: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    report = explain_definability(model, tname, max_synth_depth=0)
    cert = report.certificate_with_model(model)
    assert verify_certificate(cert, model, tname)
    assert TrustedKernel.verify(cert, model, tname)
