"""Force-directed refinement for 3D Hasse layouts."""

from __future__ import annotations

import numpy as np

from fopy.draw.poset import comparable


def _sanitize(positions: np.ndarray, velocities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if not np.isfinite(positions).all():
        positions = np.nan_to_num(positions, nan=0.0, posinf=0.0, neginf=0.0)
    if not np.isfinite(velocities).all():
        velocities = np.zeros_like(velocities)
    return positions, velocities


def simulate_forces(
    positions: np.ndarray,
    levels: np.ndarray,
    matrix: list[list[bool]],
    cover_edges: list[tuple[int, int]],
    *,
    seed: int = 42,
    iterations: int = 180,
    dt: float = 0.12,
    damping_start: float = 0.88,
    damping_end: float = 0.42,
    repulsion_strength: float = 0.55,
    comparable_attraction: float = 0.18,
    cover_attraction: float = 0.85,
    vertical_strength: float = 2.4,
    level_spacing: float = 1.0,
    phase_split: tuple[int, int, int] = (60, 60, 60),
) -> np.ndarray:
    """
    Three-phase 3D force simulation inspired by Freese/LatDraw.

    Phases:
    1. Repel incomparable elements, weak vertical anchoring.
    2. Attract comparable pairs along cover direction, stronger vertical hold.
    3. Strong cover-edge attraction with firm vertical constraint.
    """
    n = len(positions)
    pos = positions.copy()
    vel = np.zeros_like(pos)
    rng = np.random.default_rng(seed)

    cover_set = set(cover_edges)
    target_z = levels.astype(np.float64) * level_spacing

    phase1, phase2, phase3 = phase_split
    boundaries = [phase1, phase1 + phase2, phase1 + phase2 + phase3]
    total_iters = min(iterations, boundaries[2])

    for step in range(total_iters):
        if step < boundaries[0]:
            phase = 1
        elif step < boundaries[1]:
            phase = 2
        else:
            phase = 3

        cooling = 1.0 - step / max(total_iters - 1, 1)
        damping = damping_end + (damping_start - damping_end) * cooling

        forces = np.zeros_like(pos)

        # Repulsion between incomparable elements (all phases, weaker later).
        rep_scale = repulsion_strength * (1.0 if phase == 1 else 0.45 if phase == 2 else 0.2)
        for i in range(n):
            diff = pos[i] - pos
            dist_sq = (diff * diff).sum(axis=1)
            dist_sq[i] = 1.0
            for j in range(i + 1, n):
                if comparable(matrix, i, j):
                    continue
                d2 = max(float(dist_sq[j]), 0.05)
                force = rep_scale * diff[j] / d2
                forces[i] += force
                forces[j] -= force

        # Attraction along comparable pairs (not necessarily covers).
        comp_scale = comparable_attraction if phase >= 2 else 0.0
        if comp_scale > 0.0:
            for i in range(n):
                for j in range(n):
                    if i == j or not matrix[i][j]:
                        continue
                    if (i, j) in cover_set:
                        continue
                    delta = pos[j] - pos[i]
                    dist = max(float(np.linalg.norm(delta)), 0.1)
                    direction = delta / dist
                    gap = dist - level_spacing * 0.9
                    forces[i] += comp_scale * gap * direction
                    forces[j] -= comp_scale * gap * direction

        # Strong cover-edge attraction.
        cover_scale = cover_attraction if phase >= 2 else cover_attraction * 0.35
        for i, j in cover_edges:
            delta = pos[j] - pos[i]
            dist = max(float(np.linalg.norm(delta)), 0.1)
            direction = delta / dist
            desired = level_spacing * 1.05
            gap = dist - desired
            forces[i] += cover_scale * gap * direction
            forces[j] -= cover_scale * gap * direction

        # Vertical constraint toward rank level.
        v_strength = vertical_strength * (0.5 if phase == 1 else 1.0 if phase == 2 else 1.8)
        forces[:, 2] += v_strength * (target_z - pos[:, 2])

        # Light centering in xy to avoid drift.
        center = pos.mean(axis=0)
        forces[:, 0] += -0.02 * (pos[:, 0] - center[0])
        forces[:, 1] += -0.02 * (pos[:, 1] - center[1])

        vel = damping * (vel + dt * forces)
        vel += rng.normal(0.0, 0.002 * cooling, size=vel.shape)
        pos = pos + dt * vel
        pos, vel = _sanitize(pos, vel)

    return pos
