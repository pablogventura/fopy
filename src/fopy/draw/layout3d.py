"""Initial 3D node placement on level circles."""

from __future__ import annotations

import numpy as np


def initial_positions_3d(
    levels: np.ndarray,
    seed: int = 42,
    radius_scale: float = 1.0,
    perturbation: float = 0.08,
) -> np.ndarray:
    """
    Place nodes on horizontal circles, one per rank level.

    Nodes sharing a level are spaced evenly on a circle; a small random
    perturbation breaks symmetry for the force simulation.
    """
    n = len(levels)
    rng = np.random.default_rng(seed)
    positions = np.zeros((n, 3), dtype=np.float64)

    unique_levels = np.unique(levels)
    max_level = float(unique_levels.max()) if unique_levels.size else 0.0
    level_to_radius = {
        float(level): radius_scale * (1.0 + 0.35 * float(level))
        for level in unique_levels
    }

    for level in unique_levels:
        mask = levels == level
        indices = np.where(mask)[0]
        count = len(indices)
        if count == 1:
            angles = np.array([0.0])
        else:
            angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
            rng.shuffle(angles)

        radius = level_to_radius[float(level)]
        for k, idx in enumerate(indices):
            positions[idx, 0] = radius * np.cos(angles[k])
            positions[idx, 1] = radius * np.sin(angles[k])
            positions[idx, 2] = float(level)

    if perturbation > 0.0:
        noise = rng.normal(0.0, perturbation, size=(n, 3))
        noise[:, 2] *= 0.25
        positions += noise

    if max_level > 0.0:
        positions[:, 2] = levels.astype(np.float64)

    return positions
