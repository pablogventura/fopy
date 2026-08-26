"""Smoke + competition tests for DefLab partition engines."""

from __future__ import annotations

import pytest

from fopy.engines.registry import check_with_engine, normalize_fragment_engine
from fopy.finite.lindenbaum import chain_product_lattice
from fopy.finite.relops import Relation


def _diag_target(model) -> Relation:
    u = model.universe
    tuples = [(x, x) for x in u]
    return Relation("T_diag", 2, tuples)


def test_normalize_all_slugs():
    for slug in (
        "qf",
        "qf_pos",
        "ep",
        "ex",
        "pp",
        "atomic_conj",
        "fo",
        "horn",
        "gf",
        "unary_qf",
        "pattern",
    ):
        assert normalize_fragment_engine(slug) == slug or slug in {"open"}


def test_positive_split_diag_2x2():
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    result = check_with_engine(model, target, "qf_pos")
    assert result.definable is True
    assert "qf_pos" in result.fragment


def test_pp_and_atomic_agree_on_diag():
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    pp = check_with_engine(model, target, "pp", engine="split")
    ac = check_with_engine(model, target, "atomic_conj")
    assert pp.definable == ac.definable


def test_morph_split_ep_runs():
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    result = check_with_engine(model, target, "ep", engine="split")
    assert isinstance(result.definable, bool)
    assert "ep" in result.fragment


def test_gf_guarded_runs():
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    result = check_with_engine(model, target, "gf")
    assert isinstance(result.definable, bool)


def test_qf_hit_vs_merge_agree_when_merge_yes():
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    hit = check_with_engine(model, target, "qf", engine="hit")
    merge = check_with_engine(model, target, "qf", engine="merge")
    # If merge says definable, HIT should agree (soundness direction for merge purity).
    if merge.definable:
        assert hit.definable is True


@pytest.mark.parametrize("fragment", ["ex", "fo", "horn"])
def test_fragment_smoke(fragment: str):
    model = chain_product_lattice(2, 2)
    target = _diag_target(model)
    result = check_with_engine(model, target, fragment)
    assert isinstance(result.definable, bool)
