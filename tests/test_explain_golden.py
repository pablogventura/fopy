"""Golden-style expected outputs for explain (hybrid: substrings)."""

from __future__ import annotations

from pathlib import Path

import pytest

from fopy.finite import explain_definability, verify_certificate
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"
EXPECTED = Path(__file__).resolve().parent / "fixtures" / "expected" / "explain"


@pytest.mark.finite
@pytest.mark.parametrize(
    "name,definable_substr",
    [
        ("minimal.model", "definable"),
        ("cadena4.model", "definable"),
        ("retrombo_nodef.model", "not definable"),
        ("suma4.model", "not definable"),
    ],
)
def test_explain_golden_substrings(name: str, definable_substr: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    text = explain_definability(model, tname, max_synth_depth=0).pretty().lower()
    assert definable_substr in text


@pytest.mark.finite
def test_save_golden_minimal(explain_golden_dir, minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    path = explain_golden_dir / "minimal_definable.txt"
    path.write_text(report.pretty(), encoding="utf-8")
    saved = path.read_text(encoding="utf-8")
    assert "T0" in saved
    assert "definable" in saved.lower()


@pytest.mark.finite
def test_golden_file_matches_live(explain_golden_dir, minimal_model):
    report = explain_definability(minimal_model, "T0", max_synth_depth=0)
    path = explain_golden_dir / "minimal_definable.txt"
    if not path.exists():
        path.write_text(report.pretty(), encoding="utf-8")
    live = report.pretty()
    saved = path.read_text(encoding="utf-8")
    for needle in ("T0", "definable", "formula"):
        assert (needle in live.lower()) == (needle in saved.lower())


@pytest.mark.finite
def test_golden_retrombo_matches_file(explain_golden_dir):
    from fopy.parse import parse_model

    model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
    tname = next(iter(model.targets))
    report = explain_definability(model, tname, max_synth_depth=0)
    path = explain_golden_dir / "retrombo_nodef.txt"
    live = report.pretty()
    if not path.exists():
        path.write_text(live, encoding="utf-8")
    saved = path.read_text(encoding="utf-8")
    assert live.strip() == saved.strip()


@pytest.mark.finite
@pytest.mark.parametrize("name", ["minimal.model", "cadena4.model", "retrombo_nodef.model"])
def test_certificate_roundtrip_golden(name: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    report = explain_definability(model, tname, max_synth_depth=0)
    cert = report.certificate_with_model(model)
    assert verify_certificate(cert, model, tname)
