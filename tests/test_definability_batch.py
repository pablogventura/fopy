"""Batch definability smoke tests on model catalog."""

from __future__ import annotations

from pathlib import Path

import pytest

from fopy.finite import is_open_definable
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"

SMALL = [
    "minimal.model",
    "cadena4.model",
    "cadena5.model",
    "retrombo.model",
    "retrombo2.model",
    "retrombo3.model",
    "suma4.model",
    "algebra.model",
    "universo_un_elemento.model",
    "rel_0arity.model",
    "malvada.model",
    "modelomagico.model",
    "modeloqueanda.model",
    "sufrir.model",
    "miprueba.model",
]


@pytest.mark.finite
@pytest.mark.parametrize("name", SMALL)
def test_definability_smoke(name: str):
    path = MODELS / name
    if not path.exists():
        pytest.skip(name)
    model = parse_model(path, preprocess=True)
    targets = [sym for sym in model.relations if sym.startswith("T")]
    if not targets:
        pytest.skip("no target")
    if len(model.universe) > 8:
        pytest.skip("too large")
    result = is_open_definable(model, model.relations[targets[0]])
    assert isinstance(result.definable, bool)


@pytest.mark.finite
def test_definability_result_fields():
    path = Path(__file__).resolve().parent / "fixtures" / "minimal.model"
    model = parse_model(path, preprocess=True)
    targets = [s for s in model.relations if s.startswith("T")]
    assert targets
    result = is_open_definable(model, model.relations[targets[0]])
    assert isinstance(result.definable, bool)
