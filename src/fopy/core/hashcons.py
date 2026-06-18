"""Hash-consing (interning) pool for :class:`~fopy.core.basic.Basic` nodes."""

from __future__ import annotations

from typing import Any

from fopy.core.basic import Basic

_pool: dict[tuple[type[Basic], tuple[Any, ...]], Basic] = {}
_enabled = False


class _HashconsState:
    enabled = False


def enable_hashcons() -> None:
    """Turn on structural interning for supported :class:`~fopy.core.basic.Basic` nodes."""
    _HashconsState.enabled = True


def disable_hashcons() -> None:
    """Turn off structural interning."""
    _HashconsState.enabled = False


def hashcons_enabled() -> bool:
    """Return whether hash-consing is active."""
    return _HashconsState.enabled


def intern_basic(cls: type[Basic], *args: Any) -> Basic:
    """Return a canonical :class:`~fopy.core.basic.Basic` instance for ``(cls, args)``.

    Structural duplicates share identity and hash, which can speed up memoization
    and equality-heavy traversals on small symbolic ASTs.

    Args:
        cls: Concrete :class:`~fopy.core.basic.Basic` subclass to construct.
        *args: Positional arguments forwarded to ``cls.__init__`` after allocation.

    Returns:
        The interned node (existing or newly created).
    """
    key = (cls, args)
    hit = _pool.get(key)
    if hit is not None:
        return hit
    obj = object.__new__(cls)
    cls.__init__(obj, *args)
    _pool[key] = obj
    return obj


def clear_pool() -> None:
    """Drop all interned nodes (mainly for tests)."""
    _pool.clear()


def pool_size() -> int:
    """Return the number of interned nodes currently held."""
    return len(_pool)
