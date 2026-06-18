"""Property-style and cross-module integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers_finite import assert_formula_defines

import fopy as fo
from fopy.bridge import from_finite_model, to_finite_model
from fopy.finite import explain_definability, is_open_definable, synthesize_defining_formula
from fopy.finite.explain import format_open_formula, verify_certificate
from fopy.finite.open_formulas import Variable
from fopy.finite.open_parse import parse_open_formula
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
class TestCrossModuleConsistency:
    def test_explain_synthesize_agree(self, minimal_model):
        target = minimal_model.targets["T0"]
        explain = explain_definability(minimal_model, "T0", max_synth_depth=0)
        syn = synthesize_defining_formula(minimal_model, target, max_depth=2)
        if explain.definable and syn.formula is not None:
            assert_formula_defines(minimal_model, syn.formula, target)

    def test_bridge_preserves_definability(self, minimal_model):
        struct = from_finite_model(minimal_model)
        m2 = to_finite_model(struct)
        t = minimal_model.targets["T0"]
        r1 = is_open_definable(minimal_model, t)
        t2 = m2.targets.get("T0") or next(iter(m2.targets.values()))
        r2 = is_open_definable(m2, t2)
        assert r1.definable == r2.definable


@pytest.mark.finite
class TestFormatParseRoundtrip:
    @pytest.mark.parametrize(
        "src",
        [
            "true",
            "false",
            "eq(x,y)",
            "-eq(x,y)",
            "eq(f(x,y),x) & -eq(x,y)",
            "eq(x,y) | eq(f(x,y),x)",
        ],
    )
    def test_roundtrip(self, minimal_model, src: str):
        x, y = Variable.new("x"), Variable.new("y")
        vm = {"x": x, "y": y}
        f1 = parse_open_formula(src, vm, minimal_model.operations)
        s = format_open_formula(f1)
        f2 = parse_open_formula(s, vm, minimal_model.operations)
        assert f1 == f2


@pytest.mark.finite
@pytest.mark.parametrize("name", ["minimal.model", "cadena4.model", "universo_un_elemento.model"])
def test_full_pipeline(name: str):
    model = parse_model(MODELS / name, preprocess=True)
    tname = next(iter(model.targets))
    target = model.targets[tname]
    report = explain_definability(model, tname, max_synth_depth=0)
    cert = report.certificate_with_model(model)
    assert verify_certificate(cert, model, tname)
    if report.definable and report.formula:
        assert_formula_defines(model, report.formula, target)


@pytest.mark.finite
class TestPublicExports:
    def test_fo_to_nnf(self):
        x = fo.symbols("x")
        assert fo.to_nnf(fo.eq(x, x)) is not None

    def test_fo_to_prenex(self):
        x, y = fo.symbols("x y")
        assert fo.to_prenex(fo.ForAll(x, fo.eq(x, y))) is not None

    def test_finite_explain_import(self):
        from fopy import finite

        assert hasattr(finite, "explain_definability")
        assert hasattr(finite, "TrustedKernel")
        assert hasattr(finite, "synthesize_defining_formula")
