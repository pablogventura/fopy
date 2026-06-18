"""Example lattices for Hasse diagram layout."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def boolean_lattice(n: int) -> tuple[list[int], Callable[[int, int], bool]]:
    """Power-set lattice on {0,...,n-1}; elements are bitmasks."""
    if n < 0:
        raise ValueError("n must be non-negative")
    size = 2**n
    elements = list(range(size))

    def leq(a: int, b: int) -> bool:
        """Return whether bitmask ``a`` is below ``b`` in subset order."""

        return (a & b) == a

    return elements, leq


def chain(n: int) -> tuple[list[int], Callable[[int, int], bool]]:
    """Linear chain 0 < 1 < ... < n-1."""
    if n < 1:
        raise ValueError("n must be positive")
    elements = list(range(n))
    return elements, lambda a, b: a <= b


def m3() -> tuple[list[str], set[tuple[str, str]]]:
    """
    Diamond lattice M3 with three incomparable atoms.

    Hasse diagram::

            1
          / | \\
         a  b  c
          \\ | /
            0
    """
    elements = ["0", "a", "b", "c", "1"]
    covers = {
        ("0", "a"),
        ("0", "b"),
        ("0", "c"),
        ("a", "1"),
        ("b", "1"),
        ("c", "1"),
    }
    return elements, covers


def n5() -> tuple[list[str], set[tuple[str, str]]]:
    """
    Pentagon lattice N5.

    Hasse diagram::

            1
            |
            q
           / \\
          p   r
           \\ /
            0
    """
    elements = ["0", "p", "r", "q", "1"]
    covers = {
        ("0", "p"),
        ("0", "r"),
        ("p", "q"),
        ("r", "q"),
        ("q", "1"),
    }
    return elements, covers


def example_label(element: Any) -> str:
    """Human-readable label helper for examples."""
    return str(element)
