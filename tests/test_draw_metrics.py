"""Draw metrics and layout quality tests."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("matplotlib")

from fopy.draw.metrics import (
    combined_score,
    edge_crossings,
    horizontal_spread,
    min_node_distance,
    segments_intersect,
)


def test_segments_cross():
    p1, p2 = np.array([0.0, 0.0]), np.array([1.0, 1.0])
    q1, q2 = np.array([0.0, 1.0]), np.array([1.0, 0.0])
    assert segments_intersect(p1, p2, q1, q2)


def test_segments_parallel_no_cross():
    p1, p2 = np.array([0.0, 0.0]), np.array([1.0, 0.0])
    q1, q2 = np.array([0.0, 1.0]), np.array([1.0, 1.0])
    assert not segments_intersect(p1, p2, q1, q2)


def test_edge_crossings_chain():
    pos = np.array([[0.0, 0.0], [0.0, 1.0], [0.0, 2.0]])
    edges = [(0, 1), (1, 2)]
    assert edge_crossings(pos, edges) == 0


def test_min_node_distance():
    pos = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    d = min_node_distance(pos)
    assert d == pytest.approx(1.0)


def test_min_node_distance_single():
    pos = np.array([[0.0, 0.0]])
    assert min_node_distance(pos) == float("inf")


def test_horizontal_spread():
    pos = np.array([[0.0, 0.0], [3.0, 1.0]])
    assert horizontal_spread(pos) == pytest.approx(3.0)


def test_horizontal_spread_empty():
    pos = np.zeros((0, 2))
    assert horizontal_spread(pos) == 0.0


def test_combined_score_lower_for_nice_layout():
    nice = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]])
    edges = [(0, 2), (1, 2)]
    bad = np.array([[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    bad_edges = [(0, 1), (2, 3)]
    assert combined_score(nice, edges) <= combined_score(bad, bad_edges)
