"""EP ktypes: empty signature uses equality patterns (no id leakage)."""

from __future__ import annotations

from pathlib import Path

from fopy.engines.morph_split import check_morph_split
from fopy.finite.fragments.ep_ktypes import is_ep_definable
from fopy.parse import parse_model

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "models"


def test_ep_ktypes_empty_ops_matches_morph_modelo_solo_target() -> None:
    model = parse_model(FIXTURES / "modelo_solo_target.model", preprocess=True)
    target = next(iter(model.relations.values()))
    assert not model.operations
    assert is_ep_definable(model, target).definable is False
    assert check_morph_split(model, target).definable is False


def test_ep_ktypes_retrombo_may_overaccept_vs_morph() -> None:
    """Bounded EP types can still say yes when MorphOrbit says no (documented)."""
    model = parse_model(FIXTURES / "retrombo_nodef.model", preprocess=True)
    target = next(r for n, r in model.relations.items() if n.startswith("T"))
    assert model.operations
    assert check_morph_split(model, target).definable is False
    # Heuristic bound: over-accept is allowed; pin current behaviour.
    assert is_ep_definable(model, target).definable is True
