"""Curated ``.model`` fixtures for finite regression (small universes only)."""

from __future__ import annotations

from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / "fixtures" / "models"

# CORE: one definable + one non-definable tiny fixture (HIT is costly).
CORE_DEFINABILITY: tuple[str, ...] = (
    "minimal.model",
    "retrombo_nodef.model",
)

# Certificate round-trip on the same core set (no large / pathological fixtures).
CORE_CERT_MODELS: tuple[str, ...] = CORE_DEFINABILITY
