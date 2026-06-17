"""Draw module extra coverage."""

import pytest

import fopy as fo

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")


@pytest.mark.draw
def test_draw_png(tmp_path, m3_structure):
    path = tmp_path / "m3.png"
    fo.draw.draw_structure(m3_structure, filename=path)
    assert path.suffix == ".png"
    assert path.stat().st_size > 50


@pytest.mark.draw
def test_layout_retrombo(retrombo_structure):
    layout = fo.draw.layout_lattice(
        retrombo_structure.universe,
        leq=lambda a, b: retrombo_structure.call_relation("leq", (a, b)),
    )
    assert len(layout.covers) >= 3


@pytest.mark.draw
def test_hasse_from_leq_only(chain5_structure):
    elems = chain5_structure.universe
    layout = fo.draw.layout_lattice(
        elems,
        leq=lambda a, b: chain5_structure.call_relation("leq", (a, b)),
    )
    assert layout.positions_3d.shape[0] == 5
