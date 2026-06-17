"""Matplotlib rendering for Hasse diagrams."""

from __future__ import annotations

from pathlib import Path
from typing import Hashable, Sequence

import matplotlib.pyplot as plt
import numpy as np


def _label(element: Hashable) -> str:
    if isinstance(element, int) and element >= 0:
        # Bitmask subsets for boolean lattices.
        if element > 0 and (element & (element - 1)) == 0:
            bit = element.bit_length() - 1
            return f"{{{bit}}}"
        if element == 0:
            return r"$\emptyset$"
        if element > 0:
            bits = [str(i) for i in range(element.bit_length()) if element & (1 << i)]
            if bits:
                return "{" + ",".join(bits) + "}"
    return str(element)


def draw_diagram(
    elements: Sequence[Hashable],
    positions_2d: np.ndarray,
    covers: set[tuple[Hashable, Hashable]],
    *,
    ax: plt.Axes | None = None,
    node_radius: float = 0.12,
    labels: dict[Hashable, str] | None = None,
) -> plt.Axes:
    """Draw nodes and cover edges on matplotlib axes."""
    index = {element: i for i, element in enumerate(elements)}
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))

    for a, b in covers:
        i, j = index[a], index[b]
        x0, y0 = positions_2d[i]
        x1, y1 = positions_2d[j]
        dx, dy = x1 - x0, y1 - y0
        dist = max(float(np.hypot(dx, dy)), 1e-9)
        shrink = node_radius / dist
        ax.plot(
            [x0 + dx * shrink, x1 - dx * shrink],
            [y0 + dy * shrink, y1 - dy * shrink],
            color="#333333",
            linewidth=1.2,
            zorder=1,
        )

    for i, element in enumerate(elements):
        x, y = positions_2d[i]
        circle = plt.Circle((x, y), node_radius, facecolor="#4c78a8", edgecolor="#1f2d3d", zorder=2)
        ax.add_patch(circle)
        text = labels.get(element) if labels else _label(element)
        ax.text(x, y, text, ha="center", va="center", color="white", fontsize=9, zorder=3)

    pad = 0.6
    xs = positions_2d[:, 0]
    ys = positions_2d[:, 1]
    ax.set_xlim(xs.min() - pad, xs.max() + pad)
    ax.set_ylim(ys.min() - pad, ys.max() + pad)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


def save_figure(
    ax: plt.Axes,
    filename: str | Path,
    *,
    dpi: int = 150,
) -> Path:
    """Save the current axes figure to SVG or PNG based on extension."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = path.suffix.lstrip(".").lower() or "svg"
    ax.figure.savefig(path, format=fmt, bbox_inches="tight", dpi=dpi)
    plt.close(ax.figure)
    return path


def render_lattice(
    elements: Sequence[Hashable],
    positions_2d: np.ndarray,
    covers: set[tuple[Hashable, Hashable]],
    filename: str | Path | None = None,
    *,
    labels: dict[Hashable, str] | None = None,
) -> plt.Axes | Path:
    """Draw and optionally save a Hasse diagram."""
    ax = draw_diagram(elements, positions_2d, covers, labels=labels)
    if filename is not None:
        return save_figure(ax, filename)
    return ax
