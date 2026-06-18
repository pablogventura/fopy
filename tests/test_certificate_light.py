"""Light certificate verification tests (no exhaustive search)."""

from __future__ import annotations

import pytest

from fopy.finite import TrustedKernel, explain_definability, verify_certificate
from fopy.finite.explain import CERT_VERSION


@pytest.mark.finite
def test_certificate_positive(minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    cert = report.certificate()
    assert TrustedKernel.verify(cert, minimal_model, "T0")
    assert verify_certificate(cert, minimal_model, "T0")


@pytest.mark.finite
def test_certificate_tamper_fails(minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    cert = report.certificate()
    cert["definable"] = False
    assert not verify_certificate(cert, minimal_model, "T0")


@pytest.mark.finite
def test_certificate_negative_static():
    """Offline negative cert with HIT witnesses (no explain/HIT re-run)."""
    from pathlib import Path

    from fopy.parse import parse_model

    model = parse_model(
        Path(__file__).resolve().parent / "fixtures/models/retrombo_nodef.model",
        preprocess=True,
    )
    tname = next(iter(model.targets))
    cert = {
        "version": CERT_VERSION,
        "fragment": "qf",
        "definable": False,
        "witness_tuples": [[2, 3], [3, 2]],
    }
    assert not cert["definable"]
    assert TrustedKernel.verify(cert, model, tname)
