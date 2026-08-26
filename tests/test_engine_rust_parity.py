"""Parity: Rust engines vs deprecated Python engines (definable only)."""

from __future__ import annotations

import os

import pytest

from fopy.engines.registry import check_with_engine_python, normalize_fragment_engine
from fopy.finite.engine_rust import check_engine_rust, is_engine_rust_available
from fopy.finite.lindenbaum import chain_product_lattice
from fopy.finite.relops import Relation

pytestmark = pytest.mark.skipif(
    not is_engine_rust_available(),
    reason="opendefalgsplitting binary not built",
)


def _diag_target(model) -> Relation:
    u = model.universe
    return Relation("T_diag", 2, [(x, x) for x in u])


@pytest.fixture
def model_2x2():
    return chain_product_lattice(2, 2)


@pytest.mark.parametrize(
    "fragment,engine,max_depth,max_k",
    [
        ("qf_pos", "split", 2, 1),
        ("pp", "split", 2, 1),
        ("atomic_conj", "split", 1, 1),
        ("gf", "split", 2, 1),
        ("fo", "split", 2, 1),
        ("horn", "split", 2, 1),
        ("ep", "split", 2, 1),
        ("ex", "split", 2, 1),
        ("qf", "merge", 2, 1),
    ],
)
def test_rust_python_definable_parity(model_2x2, fragment, engine, max_depth, max_k):
    target = _diag_target(model_2x2)
    os.environ["FOPY_ENGINE_BACKEND"] = "python"
    try:
        with pytest.warns(DeprecationWarning):
            py = check_with_engine_python(
                model_2x2,
                target,
                fragment,
                engine=engine,  # type: ignore[arg-type]
                max_depth=max_depth,
                max_k=max_k,
            )
    finally:
        os.environ.pop("FOPY_ENGINE_BACKEND", None)

    rust = check_engine_rust(
        model_2x2,
        target,
        fragment=normalize_fragment_engine(fragment),
        engine=engine,
        max_depth=max_depth,
        max_k=max_k,
    )
    assert rust.definable == py.definable, (
        f"{fragment}/{engine}: rust={rust.definable} python={py.definable}"
    )


def test_normalize_slugs():
    assert normalize_fragment_engine("guarded") == "gf"
    assert normalize_fragment_engine("qf_pos") == "qf_pos"
