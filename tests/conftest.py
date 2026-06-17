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


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def models_dir() -> Path:
    return MODELS


@pytest.fixture
def minimal_model(fixtures_dir: Path) -> Model:
    return parse_model(fixtures_dir / "minimal.model", preprocess=False)


@pytest.fixture
def b2_structure() -> Structure:
    return fo.builders.boolean_lattice(2)


@pytest.fixture
def b3_structure() -> Structure:
    return fo.builders.b3()


@pytest.fixture
def chain5_structure() -> Structure:
    return fo.builders.chain(5)


@pytest.fixture
def m3_structure() -> Structure:
    return fo.builders.m3()


@pytest.fixture
def n5_structure() -> Structure:
    return fo.builders.n5()


@pytest.fixture
def retrombo_structure() -> Structure:
    return fo.builders.retrombo()
