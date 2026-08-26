"""Morph-orbit splitting for ep / ex."""

from __future__ import annotations

from collections.abc import Iterable

from fopy.engines._common import result_no, result_yes
from fopy.finite.definability import DefinabilityResult
from fopy.finite.fragments._partition import TuplePartition
from fopy.finite.lindenbaum import HomArrow, _morphisms
from fopy.finite.models import Model
from fopy.finite.relops import Relation


def _orbit_key_factory(arrows: list[HomArrow], universe: Iterable[int]):
    """Build a key that is constant on language-hom orbits (approx via End)."""
    # Precompute full-universe endomorphism maps when domain is whole U.
    u = frozenset(universe)
    endos = [a for a in arrows if a.domain == u]

    def key(row: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
        orbit = {row}
        changed = True
        while changed:
            changed = False
            for arrow in endos:
                for tup in list(orbit):
                    try:
                        img = arrow.vector_call(tup)
                    except ValueError:
                        continue
                    if img not in orbit:
                        orbit.add(img)
                        changed = True
        return frozenset(orbit)

    return key


def check_morph_split(model: Model, target: Relation) -> DefinabilityResult:
    """EP check: refine by orbits under language endomorphisms on U."""
    if len(model.universe) > 6:
        raise ValueError("morph-split requires |U| <= 6")
    arrows = _morphisms(model, "ep")
    partition = TuplePartition.from_model(model, target.arity)
    # Seed: also close under applying endos from each tuple (orbit key)
    key_fn = _orbit_key_factory(arrows, model.universe)
    # Cache keys (orbit computation is expensive)
    cache: dict[tuple[int, ...], frozenset[tuple[int, ...]]] = {}

    def cached_key(row: tuple[int, ...]) -> frozenset[tuple[int, ...]]:
        if row not in cache:
            cache[row] = key_fn(row)
        return cache[row]

    partition.refine(cached_key)
    if partition.is_target_pure(target):
        return result_yes(
            model, partition, target, fragment="ep", engine="morph_split", complete_for_bound=True
        )
    return result_no(partition, target, fragment="ep", engine="morph_split")


def check_embedding_split(model: Model, target: Relation) -> DefinabilityResult:
    """Existential check: refine by orbits under embeddings (open morphisms)."""
    if len(model.universe) > 6:
        raise ValueError("embedding-split requires |U| <= 6")
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
            model, partition, target, fragment="ex", engine="embedding_split", complete_for_bound=True
        )
    return result_no(partition, target, fragment="ex", engine="embedding_split")
