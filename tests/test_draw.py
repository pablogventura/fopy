"""Hasse diagram layout and rendering."""

import pytest

import fopy as fo

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")


@pytest.mark.draw
def test_layout_lattice_chain():
    layout = fo.draw.layout_lattice(list(range(5)), covers=[(i, i + 1) for i in range(4)])
    assert len(layout.elements) == 5
    assert layout.positions_2d.shape[1] == 2


@pytest.mark.draw
def test_draw_lattice_tmp(tmp_path):
    path = tmp_path / "chain.svg"
    fo.draw.draw_lattice(list(range(4)), covers=[(0, 1), (1, 2), (2, 3)], filename=path)
    assert path.exists()
    assert path.read_text().startswith("<?xml") or "<svg" in path.read_text()


@pytest.mark.draw
def test_draw_structure_from_builder(m3_structure, tmp_path):
    path = tmp_path / "m3.svg"
    fo.draw.draw_structure(m3_structure, filename=path)
    assert path.exists()
