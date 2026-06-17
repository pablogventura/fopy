"""Draw layout smoke tests on catalog structures."""

from __future__ import annotations

import pytest

import fopy as fo

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")


CATALOG = [
    ("chain3", lambda: fo.builders.chain(3)),
    ("chain6", lambda: fo.builders.chain(6)),
    ("b2", lambda: fo.builders.boolean_lattice(2)),
    ("b3", lambda: fo.builders.b3()),
    ("m3", lambda: fo.builders.m3()),
    ("n5", lambda: fo.builders.n5()),
    ("retrombo", lambda: fo.builders.retrombo()),
]


@pytest.mark.draw
@pytest.mark.parametrize("name,builder", CATALOG)
def test_layout_lattice_catalog(name: str, builder):
    s = builder()
    layout = fo.draw.layout_lattice(
        s.universe,
        leq=lambda a, b, st=s: st.call_relation("leq", (a, b)),
        seed=0,
    )
    assert len(layout.elements) == len(s.universe)
    assert layout.positions_2d.shape[0] == len(s.universe)


@pytest.mark.draw
@pytest.mark.parametrize("name,builder", CATALOG)
def test_layout_covers_only(name: str, builder):
    s = builder()
    covers = fo.builders.hasse_covers(
        list(s.universe),
        leq=lambda a, b, st=s: st.call_relation("leq", (a, b)),
    )
    layout = fo.draw.layout_lattice(list(s.universe), covers=covers, seed=1)
    assert len(layout.covers) >= 1


@pytest.mark.draw
def test_render_labels(tmp_path, b2_structure):
    layout = fo.draw.layout_lattice(
        b2_structure.universe,
        leq=lambda a, b: b2_structure.call_relation("leq", (a, b)),
    )
    labels = {e: str(e) for e in layout.elements}
    path = tmp_path / "b2.svg"
    fo.draw.render.render_lattice(
        layout.elements,
        layout.positions_2d,
        layout.covers,
        filename=path,
        labels=labels,
    )
    assert path.exists()
