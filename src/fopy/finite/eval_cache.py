"""Memoization for open-formula evaluation on finite models."""

from __future__ import annotations

from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, Variable


class EvalCache:
    """Per-model memo table for :meth:`~fopy.finite.open_formulas.Formula.satisfy`.

    Keys combine a formula node id with a sorted variable assignment so repeated
    subformula checks during HIT or extension scans reuse results.

    Attributes:
        hits: Number of cache lookups that returned a stored value.
        misses: Number of evaluations that had to run ``Formula.satisfy``.
    """

    def __init__(self) -> None:
        self._memo: dict[tuple[int, tuple[tuple[str, int], ...]], bool] = {}
        self.hits = 0
        self.misses = 0

    def clear(self) -> None:
        """Remove all cached entries and reset statistics."""
        self._memo.clear()
        self.hits = 0
        self.misses = 0

    def lookup(
        self,
        formula: Formula,
        vector: dict[Variable, int],
    ) -> bool | None:
        """Return a cached truth value or ``None`` on miss."""
        key = _cache_key(formula, vector)
        if key in self._memo:
            self.hits += 1
            return self._memo[key]
        return None

    def store(
        self,
        formula: Formula,
        vector: dict[Variable, int],
        value: bool,
    ) -> None:
        """Record the truth value of *formula* under *vector*."""
        self._memo[_cache_key(formula, vector)] = value

    def satisfy(
        self,
        formula: Formula,
        model: Model,
        vector: dict[Variable, int],
    ) -> bool:
        """Evaluate *formula* with transparent memoization.

        Args:
            formula: Open quantifier-free formula.
            model: Finite structure providing operations and relations.
            vector: Variable assignment to universe indices.

        Returns:
            Truth value of *formula* under *vector* on *model*.
        """
        cached = self.lookup(formula, vector)
        if cached is not None:
            return cached
        self.misses += 1
        value = formula.satisfy(model, vector)
        self.store(formula, vector, value)
        return value


def satisfy_cached(
    formula: Formula,
    model: Model,
    vector: dict[Variable, int],
    cache: EvalCache | None = None,
) -> bool:
    """Evaluate an open formula, optionally using a shared :class:`EvalCache`.

    Args:
        formula: Open quantifier-free formula.
        model: Finite structure.
        vector: Variable assignment.
        cache: Optional memo table; when omitted a fresh ephemeral cache is used.

    Returns:
        Truth value of *formula* under *vector*.
    """
    table = cache if cache is not None else EvalCache()
    return table.satisfy(formula, model, vector)


def _cache_key(
    formula: Formula,
    vector: dict[Variable, int],
) -> tuple[int, tuple[tuple[str, int], ...]]:
    assignment = tuple(sorted((v.sym, vector[v]) for v in vector))
    return (id(formula), assignment)
