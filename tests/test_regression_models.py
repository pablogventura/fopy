"""Regression against OpenDefAlgSplitting .model fixtures."""

from pathlib import Path

import pytest

from fopy.parse.model import parse_model

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MODELS = FIXTURES / "models"

PARSE_OK = [
    "minimal.model",
    "rel_0arity.model",
    "target_vacio.model",
    "modelo_solo_target.model",
    "universo_un_elemento.model",
    "cadena4.model",
    "cadena5.model",
    "algebra.model",
]

PARSE_FAIL = [
    "formula_vars_repetidas.model",
    "formula_con_igual.model",
]


@pytest.mark.parametrize("name", PARSE_OK)
def test_fixture_parses(name: str):
    for base in (MODELS, FIXTURES):
        path = base / name
        if path.exists():
            parse_model(path, preprocess=False)
            return
    pytest.skip(f"{name} not found")


@pytest.mark.parametrize("name", PARSE_FAIL)
def test_fixture_parse_errors(name: str):
    path = MODELS / name if (MODELS / name).exists() else FIXTURES / name
    with pytest.raises((ValueError, Exception)):
        parse_model(path, preprocess=False)

