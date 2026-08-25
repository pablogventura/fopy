"""Golden regression for EP Lindenbaum on the 2x2 chain-product lattice."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fopy.finite.lindenbaum import chain_product_lattice, join_irreducibles

pytestmark = pytest.mark.finite

GOLDEN = Path(__file__).resolve().parent / "golden" / "ep_2x2_arity3.json"


def test_ep_lindenbaum_2x2_arity3_matches_golden():
    payload = json.loads(GOLDEN.read_text(encoding="utf-8"))
    model = chain_product_lattice(2, 2)
    result = join_irreducibles(model, 3, fragment="ep", model_key="C2x2")

    assert result.count == payload["join_irreducible_count"] == 22
    assert result.fingerprints() == payload["fingerprints"]
    assert set(result.fingerprints()) == set(payload["fingerprints"])


def test_open_lindenbaum_2x2_arity2_runs():
    """Smoke: open/QF Lindenbaum via subalgebra isomorphisms on B2."""
    model = chain_product_lattice(2, 2)
    result = join_irreducibles(model, 2, fragment="open", model_key="C2x2")
    assert result.count >= 1
    assert len(result.fingerprints()) == result.count
