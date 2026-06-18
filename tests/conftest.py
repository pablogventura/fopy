"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

import fopy as fo
from fopy.finite.models import Model
from fopy.parse.model import parse_model
from fopy.structures import Structure

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MODELS = FIXTURES / "models"
EXPLAIN_GOLDEN = FIXTURES / "expected" / "explain"


@pytest.fixture
def fixtures_dir() -> Path:
    """Root ``tests/fixtures`` directory."""

    return FIXTURES


@pytest.fixture
def models_dir() -> Path:
    """Directory of regression ``.model`` files."""

    return MODELS


@pytest.fixture
def explain_golden_dir() -> Path:
    """Directory for golden explain output (created on demand)."""

    EXPLAIN_GOLDEN.mkdir(parents=True, exist_ok=True)
    return EXPLAIN_GOLDEN


@pytest.fixture
def minimal_model(fixtures_dir: Path) -> Model:
    """Two-element algebra with unary target ``T0`` (``minimal.model``)."""

    return parse_model(fixtures_dir / "minimal.model", preprocess=False)


@pytest.fixture
def b2_structure() -> Structure:
    """Boolean lattice ``B_2`` as a :class:`~fopy.structures.Structure`."""

    return fo.builders.boolean_lattice(2)


@pytest.fixture
def b3_structure() -> Structure:
    """Boolean lattice ``B_3`` (eight elements)."""

    return fo.builders.b3()


@pytest.fixture
def chain5_structure() -> Structure:
    """Linear chain of length five."""

    return fo.builders.chain(5)


@pytest.fixture
def m3_structure() -> Structure:
    """Diamond poset ``M_3``."""

    return fo.builders.m3()


@pytest.fixture
def n5_structure() -> Structure:
    """Pentagon ``N_5``."""

    return fo.builders.n5()


@pytest.fixture
def retrombo_structure() -> Structure:
    """Four-element diamond (retrombo) poset."""

    return fo.builders.retrombo()
