"""Quality metrics for projected Hasse layouts."""

from __future__ import annotations

import numpy as np


def _orientation(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    return float((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _on_segment(a: np.ndarray, b: np.ndarray, c: np.ndarray, eps: float = 1e-9) -> bool:
    return (
        min(a[0], b[0]) - eps <= c[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= c[1] <= max(a[1], b[1]) + eps
    )


def segments_intersect(p1: np.ndarray, p2: np.ndarray, q1: np.ndarray, q2: np.ndarray) -> bool:
    """True when open segments (p1,p2) and (q1,q2) properly cross."""
    o1 = _orientation(p1, p2, q1)
    o2 = _orientation(p1, p2, q2)
    o3 = _orientation(q1, q2, p1)
    o4 = _orientation(q1, q2, p2)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    eps = 1e-9
    if abs(o1) < eps and _on_segment(p1, p2, q1):
        return True
    if abs(o2) < eps and _on_segment(p1, p2, q2):
        return True
    if abs(o3) < eps and _on_segment(q1, q2, p1):
        return True
    if abs(o4) < eps and _on_segment(q1, q2, p2):
        return True
    return False


def edge_crossings(positions_2d: np.ndarray, edges: list[tuple[int, int]]) -> int:
    """Count unordered edge crossings in a 2D layout."""
    count = 0
    for i in range(len(edges)):
        a, b = edges[i]
        p1, p2 = positions_2d[a], positions_2d[b]
        for j in range(i + 1, len(edges)):
            c, d = edges[j]
            if a in (c, d) or b in (c, d):
                continue
            q1, q2 = positions_2d[c], positions_2d[d]
            if segments_intersect(p1, p2, q1, q2):
                count += 1
    return count


def min_node_distance(positions_2d: np.ndarray) -> float:
    """Minimum Euclidean distance between distinct nodes."""
    n = len(positions_2d)
    if n < 2:
        return float("inf")
    minimum = float("inf")
    for i in range(n):
        diff = positions_2d[i + 1 :] - positions_2d[i]
        if diff.size == 0:
            continue
        dist = np.sqrt((diff * diff).sum(axis=1))
        minimum = min(minimum, float(dist.min()))
    return minimum


def horizontal_spread(positions_2d: np.ndarray) -> float:
    """Horizontal extent of the layout."""
    if len(positions_2d) == 0:
        return 0.0
    return float(positions_2d[:, 0].max() - positions_2d[:, 0].min())


def combined_score(
    positions_2d: np.ndarray,
    edges: list[tuple[int, int]],
    *,
    crossing_weight: float = 10.0,
    spread_weight: float = 0.05,
    distance_penalty: float = 5.0,
    target_min_distance: float = 0.35,
) -> float:
    """
    Lower is better.

    Penalizes crossings, cramped nodes, and excessive horizontal spread.
    """
    crossings = edge_crossings(positions_2d, edges)
    spread = horizontal_spread(positions_2d)
    min_dist = min_node_distance(positions_2d)
    penalty = 0.0
    if min_dist < target_min_distance:
        penalty = distance_penalty * (target_min_distance - min_dist) ** 2
    return crossing_weight * crossings + spread_weight * spread + penalty
