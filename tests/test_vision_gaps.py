"""Smoke tests for small, well-bounded API additions."""

from __future__ import annotations

from pathlib import Path

import pytest

import fopy as fo
from fopy.finite import direct_product, verify_certificate
from fopy.universal import Congruence, quotient


def test_formula_export_methods():
    x, y = fo.symbols("x y")
    phi = fo.eq(x, y)
    assert "fof(" in phi.to_tptp()
    assert "(assert" in phi.to_smtlib()
    assert phi.latex()
    assert "fo.eq" in phi.py()


def test_many_sorted_parse_and_tptp():
    from fopy.formulas import Exists, ForAll

    phi = fo.parse_formula("forall x:U exists y:V R(x,y)", rels={"R": 2})
    assert isinstance(phi, ForAll)
    assert phi.var.sort.name == "U"
    assert isinstance(phi.body, Exists)
    assert phi.body.var.sort.name == "V"
    assert "y:V" in phi.to_tptp()


def test_structure_universes():
    from fopy.sorts import Sort

    sig = fo.Signature()
    s = fo.Structure(
        sig,
        universe=[0, 1],
        universes={"U": [0, 1], "V": [0]},
    )
    assert s.universe_for("U") == [0, 1]
    assert s.universe_for(Sort("V")) == [0]


@pytest.mark.finite
def test_definability_namespace(minimal_model):
    from fopy.finite import Definability

    tname = next(iter(minimal_model.targets))
    result = Definability.check(minimal_model, tname, fragment="qf")
    assert result.definable
    report = Definability.explain(minimal_model, tname, max_synth_depth=0)
    assert report.definable


def test_certificate_v2(minimal_model):
    from fopy.finite import Definability, verify_certificate

    tname = next(iter(minimal_model.targets))
    report = Definability.explain(minimal_model, tname, max_synth_depth=0)
    cert = report.certificate()
    assert cert["version"] == 2
    assert verify_certificate(cert, minimal_model, tname)


@pytest.mark.finite
def test_direct_product_chain():
    from fopy.bridge import to_finite_model

    m2 = to_finite_model(fo.builders.chain(2))
    m3 = to_finite_model(fo.builders.chain(3))
    prod = direct_product(m2, m3)
    assert len(prod.universe) == 6


@pytest.mark.finite
def test_quotient_trivial(minimal_model):
    c = Congruence(classes=(frozenset(minimal_model.universe),))
    q = quotient(minimal_model, c)
    assert len(q.universe) == 1


@pytest.mark.finite
def test_retrombo_certificate_verify():
    from fopy.parse import parse_model

    model = parse_model(
        Path(__file__).resolve().parent / "fixtures/models/retrombo_nodef.model",
        preprocess=True,
    )
    tname = next(iter(model.targets))
    cert = {
        "version": 1,
        "fragment": "qf",
        "definable": False,
        "witness_tuples": [[2, 3], [3, 2]],
    }
    assert verify_certificate(cert, model, tname)


def test_alpha_equivalent():
    x, y = fo.symbols("x y")
    a = fo.forall(x, fo.eq(x, y))
    b = fo.forall(y, fo.eq(y, x))
    assert fo.alpha_equivalent(a, b)


def test_api_aliases():
    from fopy.api import Function, Relation, Vars

    x, y = Vars("x y")
    assert Function("f", 2).arity == 2
    assert Relation("R", 2).arity == 2
    assert x.sym == "x" and y.sym == "y"


@pytest.mark.finite
def test_lattice_draw_wrapper(minimal_model):
    from fopy.universal import congruence_lattice, subalgebra_lattice

    cl = congruence_lattice(minimal_model)
    sl = subalgebra_lattice(minimal_model)
    assert len(cl) >= 1
    assert len(sl) >= 1
    assert hasattr(cl, "draw")
    assert hasattr(sl, "draw")


def test_hashcons_variables():
    from fopy.core.hashcons import clear_pool, disable_hashcons, enable_hashcons, pool_size
    from fopy.symbols import Variable

    disable_hashcons()
    clear_pool()
    a = Variable("x")
    b = Variable("x")
    assert a is not b
    enable_hashcons()
    clear_pool()
    c = Variable("x")
    d = Variable("x")
    assert c is d
    assert pool_size() >= 1
    disable_hashcons()
    clear_pool()


def test_plugins_registry():
    from fopy.plugins import get, list_plugins

    names = list_plugins()
    assert "solver.z3" in names
    assert "fragment.check" in names
    assert callable(get("solver.z3"))
