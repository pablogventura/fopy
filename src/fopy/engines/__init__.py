"""Partition engines: splitting / merging definability backends."""

from __future__ import annotations

from fopy.engines.atomic_split import check_atomic_conj, check_pp_split
from fopy.engines.guarded_split import check_guarded
from fopy.engines.iso_merge import check_qf_merge
from fopy.engines.morph_split import check_embedding_split, check_morph_split
from fopy.engines.positive_split import check_positive_split
from fopy.engines.registry import ALL_FRAGMENTS, check_with_engine, normalize_fragment_engine

__all__ = [
    "ALL_FRAGMENTS",
    "check_atomic_conj",
    "check_embedding_split",
    "check_guarded",
    "check_morph_split",
    "check_positive_split",
    "check_pp_split",
    "check_qf_merge",
    "check_with_engine",
    "normalize_fragment_engine",
]
