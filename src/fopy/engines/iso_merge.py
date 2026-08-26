"""QF IsoType-style merging: saturate under open morphisms then purity."""

from __future__ import annotations

from fopy.engines._common import result_no, result_yes
from fopy.engines.morph_split import _orbit_key_factory
from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.lindenbaum import _morphisms
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def check_qf_merge(model: Model, target: Relation) -> DefinabilityResult:
    """Merging engine for ``qf``: partition by open-morphism orbits (IsoType-ish).

    Empirical competitor to HIT splitting. Sound for purity under open
    preservation; not claimed complete vs full Campercholi without further work.
    """
    if len(model.universe) > 6:
        raise ValueError("qf merge requires |U| <= 6")
    arrows = _morphisms(model, "open")
    partition = TuplePartition.from_model(model, target.arity)
    key_fn = _orbit_key_factory(arrows, model.universe)
    cache: dict[tuple[int, ...], frozenset[tuple[int, ...]]] = {}

    def cached_key(row: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
        if row not in cache:
            cache[row] = key_fn(row)
        return cache[row]

    partition.refine(cached_key)
    if partition.is_target_pure(target):
        return result_yes(
            model, partition, target, fragment="qf", engine="iso_merge", complete_for_bound=False
        )
    return result_no(partition, target, fragment="qf", engine="iso_merge")
