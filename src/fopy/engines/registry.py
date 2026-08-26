"""Fragment + engine registry for DefLab.

Default backend is Rust (`OpenDefAlgSplitting`) when available.
Python engines are deprecated: set ``FOPY_ENGINE_BACKEND=python`` only for
parity / emergency fallback.
"""

from __future__ import annotations

import os
import warnings
from typing import Literal

from fopy.engines.atomic_split import check_atomic_conj, check_pp_split
from fopy.engines.guarded_split import check_guarded
from fopy.engines.iso_merge import check_qf_merge
from fopy.engines.morph_split import check_embedding_split, check_morph_split
from fopy.engines.positive_split import check_positive_split
from fopy.finite.definability import DefinabilityResult, is_open_definable
from fopy.finite.fragments import check_fragment
from fopy.finite.hit import HitConfig
from fopy.finite.models import Model
from fopy.finite.relops import Relation

EngineKind = Literal["split", "merge", "auto", "ktypes", "hit"]

ALL_FRAGMENTS = frozenset(
    {
        "qf",
        "open",
        "quantifier-free",
        "qf_pos",
        "ep",
        "ex",
        "pp",
        "atomic_conj",
        "fo",
        "horn",
        "gf",
        "guarded",
        "unary_qf",
        "pattern",
    }
)

_PYTHON_ENGINE_WARNING = (
    "fopy.engines Python backends are deprecated; prefer Rust "
    "(OpenDefAlgSplitting). Set FOPY_ENGINE_BACKEND=python only for parity."
)


def normalize_fragment_engine(fragment: str) -> str:
    """Canonical fragment slug for engines."""
    key = fragment.strip().lower().replace("-", "_")
    aliases = {
        "open": "qf",
        "quantifier_free": "qf",
        "quantifierfree": "qf",
        "qfpos": "qf_pos",
        "positive": "qf_pos",
        "existential_positive": "ep",
        "existential": "ex",
        "atomic": "atomic_conj",
        "guarded": "gf",
        "unary": "unary_qf",
    }
    key = aliases.get(key, key)
    if key not in {
        "qf",
        "qf_pos",
        "ep",
        "ex",
        "pp",
        "atomic_conj",
        "fo",
        "horn",
        "gf",
        "unary_qf",
        "pattern",
    }:
        supported = ", ".join(
            sorted(
                {
                    "qf",
                    "qf_pos",
                    "ep",
                    "ex",
                    "pp",
                    "atomic_conj",
                    "fo",
                    "horn",
                    "gf",
                    "unary_qf",
                    "pattern",
                }
            )
        )
        raise NotImplementedError(
            f"Fragment {fragment!r} is not supported. Supported: {supported}."
        )
    return key


def check_with_engine_python(
    model: Model,
    target: Relation,
    fragment: str,
    *,
    engine: EngineKind = "auto",
    **kwargs: object,
) -> DefinabilityResult:
    """Deprecated Python oracle (parity / emergency)."""
    warnings.warn(_PYTHON_ENGINE_WARNING, DeprecationWarning, stacklevel=2)
    frag = normalize_fragment_engine(fragment)
    eng: EngineKind = engine

    def _int(name: str, default: int) -> int:
        value = kwargs.get(name, default)
        return value if isinstance(value, int) else default

    if frag in ("unary_qf", "pattern"):
        config = kwargs.get("config")
        hit_cfg = config if isinstance(config, HitConfig) else None
        result = is_open_definable(model, target, hit_cfg)
        result.fragment = f"qf:{frag}"
        return result

    if frag == "qf":
        if eng == "merge":
            return check_qf_merge(model, target)
        if eng in ("split", "hit", "auto"):
            config = kwargs.get("config")
            hit_cfg = config if isinstance(config, HitConfig) else None
            result = is_open_definable(model, target, hit_cfg)
            result.fragment = "qf:hit_split"
            return result
        raise NotImplementedError("qf has no ktypes engine; use split (HIT) or merge")

    if frag == "qf_pos":
        return check_positive_split(model, target)
    if frag == "ep":
        if eng == "ktypes":
            return check_fragment(model, target, "ep", **kwargs)
        return check_morph_split(model, target)
    if frag == "ex":
        return check_embedding_split(model, target)
    if frag == "pp":
        if eng == "ktypes":
            return check_fragment(model, target, "pp", **kwargs)
        return check_pp_split(model, target, max_depth=_int("max_depth", 2))
    if frag == "atomic_conj":
        return check_atomic_conj(model, target, max_depth=_int("max_depth", 1))
    if frag == "gf":
        return check_guarded(model, target, max_k=_int("max_k", 1))
    if frag == "fo":
        return check_fragment(model, target, "fo", **kwargs)
    if frag == "horn":
        return check_fragment(model, target, "horn", **kwargs)
    raise NotImplementedError(f"No engine for fragment {frag!r}")


def check_with_engine(
    model: Model,
    target: Relation,
    fragment: str,
    *,
    engine: EngineKind = "auto",
    **kwargs: object,
) -> DefinabilityResult:
    """Dispatch definability check (Rust default, Python if forced/unavailable)."""
    from fopy.finite.engine_rust import check_engine_rust, prefer_rust_backend

    frag = normalize_fragment_engine(fragment)
    eng: EngineKind = engine

    def _int(name: str, default: int) -> int:
        value = kwargs.get(name, default)
        return value if isinstance(value, int) else default

    # HIT qf split stays on existing HIT path (Rust HIT or Python HIT).
    if frag == "qf" and eng in ("split", "hit", "auto"):
        config = kwargs.get("config")
        hit_cfg = config if isinstance(config, HitConfig) else None
        result = is_open_definable(model, target, hit_cfg)
        result.fragment = "qf:hit_split"
        return result

    if frag in ("unary_qf", "pattern"):
        config = kwargs.get("config")
        hit_cfg = config if isinstance(config, HitConfig) else None
        result = is_open_definable(model, target, hit_cfg)
        result.fragment = f"qf:{frag}"
        return result

    if prefer_rust_backend():
        rust_engine = eng if eng != "auto" else "split"
        if frag == "qf" and eng == "merge":
            rust_engine = "merge"
        try:
            timeout_raw = kwargs.get("timeout_s", 120.0)
            timeout_s = float(timeout_raw) if isinstance(timeout_raw, (int, float)) else 120.0
            return check_engine_rust(
                model,
                target,
                fragment=frag,
                engine=rust_engine,
                max_depth=_int("max_depth", 2 if frag != "atomic_conj" else 1),
                max_k=_int("max_k", 1),
                timeout_s=timeout_s,
            )
        except Exception:
            # Explicit rust request: do not fall back to deprecated Python
            # (can hang / OOM on fo/horn). auto mode may still fall through.
            if os.environ.get("FOPY_ENGINE_BACKEND", "").strip().lower() == "rust":
                raise
            # Fall through to deprecated Python for parity resilience.
            pass

    return check_with_engine_python(model, target, fragment, engine=eng, **kwargs)
