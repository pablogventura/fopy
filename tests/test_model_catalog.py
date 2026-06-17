"""Parse all model fixtures that should succeed."""

from __future__ import annotations

from pathlib import Path

import pytest

from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"

SKIP = {
    "formula_con_igual.model",
    "formula_vars_repetidas.model",
    "retromboconformula.model",
    "suma4formula.model",
    "romboletras.model",
    "modelobmagico.model",
}

ALL_MODELS = sorted(p.name for p in MODELS.glob("*.model"))


@pytest.mark.parametrize("name", [n for n in ALL_MODELS if n not in SKIP])
def test_model_parses(name: str):
    m = parse_model(MODELS / name, preprocess=False)
    assert len(m.universe) >= 1


@pytest.mark.parametrize("name", sorted(SKIP))
def test_model_parse_failures(name: str):
    with pytest.raises(Exception):
        parse_model(MODELS / name, preprocess=False)


@pytest.mark.parametrize("name", [n for n in ALL_MODELS if n not in SKIP])
def test_model_preprocess(name: str):
    m = parse_model(MODELS / name, preprocess=True)
    assert m.universe == sorted(set(m.universe))


@pytest.mark.parametrize("name", ["minimal.model", "cadena4.model", "algebra.model"])
def test_model_has_operations_or_relations(name: str):
    m = parse_model(MODELS / name, preprocess=False)
    assert m.operations or m.relations
