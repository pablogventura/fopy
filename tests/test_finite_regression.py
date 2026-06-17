"""Open definability regression against known fixtures."""

from pathlib import Path

import pytest

from fopy.finite import is_open_definable
from fopy.parse import parse_model

MODELS = Path(__file__).resolve().parent / "fixtures" / "models"

# Expected definability (universe size <= 6, preprocessed targets)
EXPECTED_DEFINABLE = {
    "minimal.model": True,
    "cadena4.model": True,
    "cadena5.model": True,
    "universo_un_elemento.model": True,
    "rel_0arity.model": True,
    "retrombo.model": True,
    "retrombo_nodef.model": False,
    "retrombo_nodef_sinpura.model": False,
    "suma4.model": False,
    "algebra.model": False,
    "miprueba.model": False,
}


@pytest.mark.finite
@pytest.mark.parametrize("name,expected", EXPECTED_DEFINABLE.items())
def test_definability_regression(name: str, expected: bool):
    path = MODELS / name
    if not path.exists():
        path = Path(__file__).resolve().parent / "fixtures" / name
    model = parse_model(path, preprocess=True)
    targets = [sym for sym in model.relations if sym.startswith("T")]
    assert targets, f"No target in {name}"
    result = is_open_definable(model, model.relations[targets[0]])
    assert result.definable is expected, name


@pytest.mark.parametrize("name", sorted(p.name for p in MODELS.glob("*.model")))
def test_all_models_parse_or_expected_fail(name: str):
    path = MODELS / name
    fail_names = {
        "formula_con_igual.model",
        "formula_vars_repetidas.model",
        "retromboconformula.model",
        "suma4formula.model",
        "romboletras.model",
        "modelobmagico.model",
    }
    if name in fail_names:
        with pytest.raises(Exception):
            parse_model(path, preprocess=False)
    else:
        parse_model(path, preprocess=False)
