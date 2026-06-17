"""3D to 2D projection and view selection."""

from __future__ import annotations

import math

import numpy as np

from fopy.draw.metrics import combined_score


def projection_matrix(azimuth_deg: float, elevation_deg: float) -> np.ndarray:
    """Return a 3x3 rotation matrix for spherical viewing angles."""
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    cos_az, sin_az = math.cos(az), math.sin(az)
    cos_el, sin_el = math.cos(el), math.sin(el)

    rot_z = np.array(
        [[cos_az, -sin_az, 0.0], [sin_az, cos_az, 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    rot_x = np.array(
        [[1.0, 0.0, 0.0], [0.0, cos_el, -sin_el], [0.0, sin_el, cos_el]],
        dtype=np.float64,
    )
    return rot_x @ rot_z


def project_3d_to_2d(
    positions_3d: np.ndarray,
    azimuth_deg: float = 35.0,
    elevation_deg: float = 25.0,
) -> np.ndarray:
    """Orthographic projection after rotation."""
    matrix = projection_matrix(azimuth_deg, elevation_deg)
    rotated = positions_3d @ matrix.T
    return rotated[:, :2].copy()


def find_best_view(
    positions_3d: np.ndarray,
    edges: list[tuple[int, int]],
    *,
    azimuth_steps: int = 24,
    elevation_angles: tuple[float, ...] = (15.0, 25.0, 35.0, 45.0),
) -> tuple[float, float, np.ndarray]:
    """
    Scan viewing angles and return the best azimuth, elevation, and 2D layout.
    """
    best_score = float("inf")
    best_az = 35.0
    best_el = 25.0
    best_pos = project_3d_to_2d(positions_3d, best_az, best_el)

    for el in elevation_angles:
        for step in range(azimuth_steps):
            az = 360.0 * step / azimuth_steps
            pos2d = project_3d_to_2d(positions_3d, az, el)
            score = combined_score(pos2d, edges)
            if score < best_score:
                best_score = score
                best_az = az
                best_el = el
                best_pos = pos2d

    return best_az, best_el, best_pos
