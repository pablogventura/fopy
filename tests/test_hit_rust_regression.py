"""Regression tests for OpenDefAlgSplitting (Rust HIT) backend."""

from __future__ import annotations

import pytest

import fopy as fo
from fopy.bridge import to_finite_model
from fopy.finite import is_open_definable
from fopy.finite.hit_rust import find_opendefalgsplitting_binary, resolve_hit_backend
from fopy.finite.relops import Relation
from fopy.signature import Signature

pytestmark = pytest.mark.finite

requires_rust = pytest.mark.skipif(
    find_opendefalgsplitting_binary() is None,
    reason="OpenDefAlgSplitting binary not available",
)


def _bool_magma_model():
    sig = Signature(functions={"and": 2})
    struct = fo.builders.from_cayley(sig, "and", [0, 1], [[0, 0], [0, 1]])
    return to_finite_model(struct)


def _b2_model():
    return to_finite_model(fo.builders.boolean_lattice(2))


def _unary_target(elems: list[int]) -> Relation:
    rel = Relation("T0", 1)
    for elem in elems:
        rel.add([elem])
    return rel


@requires_rust
def test_hit_backend_defaults_to_rust():
    assert resolve_hit_backend() == "rust"


@requires_rust
@pytest.mark.parametrize(
    "elems,expected",
    [
        ([], True),
        ([0, 1], True),
        ([0], False),
        ([1], False),
    ],
)
def test_bool_magma_unary_regression(elems: list[int], expected: bool):
    model = _bool_magma_model()
    result = is_open_definable(model, _unary_target(elems))
    assert result.definable is expected


@requires_rust
@pytest.mark.parametrize(
    "elems",
    [
        [0],
        [3],
        [1, 2],
    ],
)
def test_b2_lattice_unary_not_definable(elems: list[int]):
    model = _b2_model()
    result = is_open_definable(model, _unary_target(elems))
    assert result.definable is False


@requires_rust
def test_b2_lattice_empty_unary_definable():
    model = _b2_model()
    result = is_open_definable(model, _unary_target([]))
    assert result.definable is True


@requires_rust
def test_b2_lattice_full_unary_definable():
    model = _b2_model()
    result = is_open_definable(model, _unary_target([0, 1, 2, 3]))
    assert result.definable is True
