"""Simple plugin registry for optional backends."""

from __future__ import annotations

from typing import Any

_REGISTRY: dict[str, Any] = {}


def register(name: str, plugin: Any) -> None:
    """Register a plugin under *name*.

    Args:
        name: Lookup key (overwrites any existing entry).
        plugin: Callable, class, or module object to store.
    """
    _REGISTRY[name] = plugin


def get(name: str) -> Any:
    """Return the plugin registered as *name*.

    Args:
        name: Lookup key.

    Returns:
        Registered object.

    Raises:
        KeyError: If *name* is not registered.
    """
    return _REGISTRY[name]


def unregister(name: str) -> None:
    """Remove a plugin from the registry.

    Args:
        name: Lookup key.

    Raises:
        KeyError: If *name* is not registered.
    """
    del _REGISTRY[name]


def list_plugins() -> list[str]:
    """Return sorted names of all registered plugins."""
    return sorted(_REGISTRY)


def call(name: str, *args: Any, **kwargs: Any) -> Any:
    """Invoke a registered callable plugin.

    Args:
        name: Registry key.
        *args: Positional arguments forwarded to the plugin.
        **kwargs: Keyword arguments forwarded to the plugin.

    Returns:
        Result of ``plugin(*args, **kwargs)``.

    Raises:
        KeyError: If *name* is not registered.
        TypeError: If the registered object is not callable.
    """
    plugin = get(name)
    if not callable(plugin):
        raise TypeError(f"Plugin {name!r} is not callable")
    fn = plugin
    return fn(*args, **kwargs)


def clear() -> None:
    """Remove every entry from the registry (mainly for tests)."""
    _REGISTRY.clear()


def _register_builtin_plugins() -> None:
    """Register default optional backends (idempotent)."""
    from fopy.solvers.z3_backend import z3_available

    register("solver.z3", z3_available)
    try:
        from fopy.draw.mermaid_export import hasse_to_mermaid

        register("viz.mermaid", hasse_to_mermaid)
    except ImportError:
        pass

    def _fragment_check(model: object, target: object, fragment: str, **kwargs: object) -> object:
        from fopy.finite.definability import check_definability
        from fopy.finite.models import Model
        from fopy.finite.relops import Relation

        if not isinstance(model, Model):
            raise TypeError("model must be a finite Model")
        tgt: Relation | str = target if isinstance(target, (Relation, str)) else str(target)
        return check_definability(model, tgt, fragment=fragment, **kwargs)

    register("fragment.check", _fragment_check)


_register_builtin_plugins()
