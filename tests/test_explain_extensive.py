"""Extensive tests for fopy.finite.explain."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers_finite import assert_explain_agrees_with_check, assert_formula_defines

from fopy.bridge import from_finite_model, to_finite_model
from fopy.finite.explain import (
    CERT_VERSION,
    ExplainReport,
    Obstruction,
    atomic_type,
    check_definability,
    explain_definability,
    explain_obstruction,
    format_open_formula,
    latex_open_formula,
    model_fingerprint,
    normalize_fragment,
    resolve_target,
    verify_certificate,
)
from fopy.finite.hit import Counterexample
from fopy.finite.open_formulas import Term, Variable, eq, false_formula, true_formula
from fopy.finite.open_parse import parse_open_formula
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"


@pytest.mark.finite
class TestNormalizeFragment:
    @pytest.mark.parametrize("frag", ["qf", "open", "quantifier-free", " QF ", "OPEN"])
    def test_aliases(self, frag: str):
        assert normalize_fragment(frag) == "qf"

    @pytest.mark.parametrize("frag", ["pp", "ep", "horn", "fo"])
    def test_ktype_fragments(self, frag: str):
        assert normalize_fragment(frag) == frag

    @pytest.mark.parametrize("frag", ["", "mso"])
    def test_unsupported(self, frag: str):
        with pytest.raises(NotImplementedError):
            normalize_fragment(frag)


@pytest.mark.finite
class TestResolveTarget:
    def test_by_name_targets(self, minimal_model):
        rel = resolve_target(minimal_model, "T0")
        assert rel.sym == "T0"

    def test_by_relation_object(self, minimal_model):
        t = minimal_model.targets["T0"]
        assert resolve_target(minimal_model, t) is t

    def test_missing_raises(self, minimal_model):
        with pytest.raises(KeyError):
            resolve_target(minimal_model, "T99")


@pytest.mark.finite
class TestFormatOpenFormula:
    def test_true_false(self):
        assert format_open_formula(true_formula(None)) == "true"
        assert format_open_formula(false_formula(None)) == "false"

    def test_eq_and_neg(self, minimal_model):
        ops = minimal_model.operations
        x, y = Variable.new("x"), Variable.new("y")
        f = parse_open_formula("eq(f(x,y),x) & -eq(x,y)", {"x": x, "y": y}, ops)
        s = format_open_formula(f)
        assert "eq(" in s

    def test_latex_eq(self):
        x = Term.from_variable(Variable.new("x"))
        y = Term.from_variable(Variable.new("y"))
        out = latex_open_formula(eq(x, y))
        assert "=" in out


@pytest.mark.finite
class TestAtomicType:
    def test_deterministic(self, minimal_model):
        a = atomic_type(minimal_model, (0, 1))
        b = atomic_type(minimal_model, (0, 1))
        assert a == b

    def test_differs_for_diff_tuples(self, minimal_model):
        a = atomic_type(minimal_model, (0, 0))
        b = atomic_type(minimal_model, (1, 0))
        assert a != b

    def test_max_depth(self, minimal_model):
        shallow = atomic_type(minimal_model, (0, 0), max_depth=0)
        deep = atomic_type(minimal_model, (0, 0), max_depth=2)
        assert len(deep) >= len(shallow)


@pytest.mark.finite
class TestModelFingerprint:
    def test_stable(self, minimal_model):
        assert model_fingerprint(minimal_model) == model_fingerprint(minimal_model)

    def test_changes_with_ops(self, minimal_model):
        fp1 = model_fingerprint(minimal_model)
        m2 = parse_model(MODELS / "cadena4.model", preprocess=False)
        assert model_fingerprint(m2) != fp1


@pytest.mark.finite
class TestExplainReport:
    def test_from_check_definable(self, minimal_model):
        from fopy.finite import is_open_definable

        target = minimal_model.targets["T0"]
        result = is_open_definable(minimal_model, target)
        report = ExplainReport.from_check(result, minimal_model, target, "qf")
        assert report.definable == result.definable
        assert report.target_sym == "T0"

    def test_pretty_contains_target(self, minimal_model):
        report = explain_definability(minimal_model, "T0", max_synth_depth=0)
        assert "T0" in report.pretty()

    def test_latex_obstruction_when_not_definable(self):
        model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
        tname = next(iter(model.targets))
        report = explain_definability(model, tname, max_synth_depth=0)
        if not report.definable:
            assert "Obstruction" in report.latex()

    def test_proof_sketch_non_empty(self, minimal_model):
        assert explain_definability(minimal_model, "T0", max_synth_depth=0).proof_sketch()

    def test_counterexample_table_header(self):
        model = parse_model(MODELS / "retrombo_nodef.model", preprocess=True)
        tname = next(iter(model.targets))
        table = explain_definability(model, tname, max_synth_depth=0).counterexample_table()
        assert "tuple" in table

    def test_certificate_schema(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        assert cert["version"] == CERT_VERSION
        assert "fragment" in cert
        assert "definable" in cert

    def test_certificate_with_model_fingerprint(self, minimal_model):
        report = explain_definability(minimal_model, "T0", max_synth_depth=0)
        cert = report.certificate_with_model(minimal_model)
        assert cert["model_fingerprint"] is not None

    def test_repr_html(self, minimal_model):
        html = explain_definability(minimal_model, "T0", max_synth_depth=0)._repr_html_()
        assert "<div" in html and "definable" in html and "<details" in html

    def test_minimal_fields_when_definable(self, minimal_model):
        report = explain_definability(minimal_model, "T0", max_synth_depth=2)
        assert report.definable
        assert report.formula_minimal is True
        assert report.min_term_depth is not None
        assert "Minimal term depth" in report.pretty() or report.min_term_depth >= 0


@pytest.mark.finite
class TestExplainObstruction:
    def test_message_mentions_not_definable(self, minimal_model):
        target = minimal_model.targets["T0"]
        ce = Counterexample([[0, 0], [1, 0]])
        obs = explain_obstruction(minimal_model, target, ce)
        assert isinstance(obs, Obstruction)
        assert "not definable" in obs.message.lower()

    def test_witness_pair_fields(self, minimal_model):
        target = minimal_model.targets["T0"]
        ce = Counterexample([[0, 0], [1, 0]])
        obs = explain_obstruction(minimal_model, target, ce)
        assert obs.tuple_in
        assert obs.tuple_out


@pytest.mark.finite
class TestVerifyCertificate:
    def test_bad_version(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        cert["version"] = 99
        assert not verify_certificate(cert, minimal_model, "T0")

    def test_bad_fingerprint(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        cert["model_fingerprint"] = "deadbeef"
        assert not verify_certificate(cert, minimal_model, "T0")

    def test_tamper_formula(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        cert["formula"] = "false"
        assert not verify_certificate(cert, minimal_model, "T0")

    def test_negative_witness_same_membership_fails(self, minimal_model):
        cert = {
            "version": CERT_VERSION,
            "definable": False,
            "witness_tuples": [[0, 0], [0, 0]],
        }
        assert not verify_certificate(cert, minimal_model, "T0")

    def test_non_bool_definable(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        cert["definable"] = "yes"
        assert not verify_certificate(cert, minimal_model, "T0")


@pytest.mark.finite
class TestExplainDefinibilityIntegration:
    @pytest.mark.parametrize(
        "name",
        [
            "minimal.model",
        ],
    )
    def test_agrees_with_check(self, name: str):
        model = parse_model(MODELS / name, preprocess=True)
        if not model.targets:
            pytest.skip("no target")
        tname = next(iter(model.targets))
        assert_explain_agrees_with_check(model, model.targets[tname])

    def test_structure_input(self, minimal_model):
        struct = from_finite_model(minimal_model)
        report = explain_definability(struct, "T0", max_synth_depth=0)
        assert isinstance(report.definable, bool)

    def test_roundtrip_model(self, minimal_model):
        m2 = to_finite_model(from_finite_model(minimal_model))
        r1 = explain_definability(minimal_model, "T0", max_synth_depth=0)
        r2 = explain_definability(m2, "T0", max_synth_depth=0)
        assert r1.definable == r2.definable

    def test_check_definability_alias(self, minimal_model):
        assert check_definability is not None
        target = minimal_model.targets["T0"]
        from fopy.finite import is_open_definable

        assert (
            check_definability(minimal_model, target).definable
            == is_open_definable(minimal_model, target).definable
        )

    def test_definable_formula_extension(self, minimal_model):
        report = explain_definability(minimal_model, "T0", max_synth_depth=0)
        if report.definable and report.formula:
            assert_formula_defines(minimal_model, report.formula, minimal_model.targets["T0"])

    def test_fragment_open_alias(self, minimal_model):
        r1 = explain_definability(minimal_model, "T0", max_synth_depth=0, fragment="qf")
        r2 = explain_definability(minimal_model, "T0", max_synth_depth=0, fragment="open")
        assert r1.definable == r2.definable

    def test_certificate_json_serializable(self, minimal_model):
        cert = explain_definability(minimal_model, "T0", max_synth_depth=0).certificate()
        blob = json.dumps(cert)
        loaded = json.loads(blob)
        assert verify_certificate(loaded, minimal_model, "T0")
