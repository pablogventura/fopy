"""Rank levels for Hasse diagram vertical placement."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RankLevels:
    """Vertical rank assignment for poset elements."""

    levels: np.ndarray
    height: np.ndarray
    depth: np.ndarray
    rank: np.ndarray


def _longest_paths(matrix: list[list[bool]], forward: bool) -> np.ndarray:
    """Longest chain lengths; forward=True counts from minimals upward."""
    n = len(matrix)
    adj = np.array(matrix, dtype=bool)
    if not forward:
        adj = adj.T
    dist = np.zeros(n, dtype=np.int64)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            preds = np.where(adj[:, i])[0]
            preds = preds[preds != i]
            candidate = 0 if preds.size == 0 else int(dist[preds].max() + 1)
            if candidate > dist[i]:
                dist[i] = candidate
                changed = True
    return dist


def compute_levels(matrix: list[list[bool]]) -> RankLevels:
    """
    Assign integer levels using height (from bottom) as primary rank.

    Height is the longest chain from a minimal element; depth is the longest
    chain to a maximal element. Rank equals height for drawing.
    """
    height = _longest_paths(matrix, forward=True)
    depth = _longest_paths(matrix, forward=False)
    rank = height.copy()
    levels = rank.astype(np.float64)
    return RankLevels(levels=levels, height=height, depth=depth, rank=rank)


def normalize_levels(levels: np.ndarray) -> np.ndarray:
    """Shift levels so the minimum is zero."""
    return levels - float(levels.min())
