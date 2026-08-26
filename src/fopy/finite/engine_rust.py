"""Rust DefLab engine bridge (parity with OpenDefAlgSplitting --fragment)."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from fopy.finite.definability import DefinabilityResult
from fopy.finite.hit_rust import find_opendefalgsplitting_binary
from fopy.finite.models import Model
from fopy.finite.relops import Relation
from fopy.parse.write_model import write_model

_DEFINABLE_RE = re.compile(r"\bDEFINABLE\b")
_NOT_DEFINABLE_RE = re.compile(r"NOT DEFINABLE")
_META_RE = re.compile(r"# meta:\s*(\{.*\})")


def is_engine_rust_available() -> bool:
    return find_opendefalgsplitting_binary() is not None


def check_engine_rust(
    model: Model,
    target: Relation,
    *,
    fragment: str,
    engine: str = "auto",
    max_depth: int = 2,
    max_k: int = 1,
    timeout_s: float = 120.0,
) -> DefinabilityResult:
    """Run Rust engine; return definability verdict."""
    bin_path = find_opendefalgsplitting_binary()
    if bin_path is None:
        raise FileNotFoundError("opendefalgsplitting binary not found")

    isolated = Model(
        universe=list(model.universe),
        operations=dict(model.operations),
        relations={},
        targets={target.sym: target},
    )
    with tempfile.TemporaryDirectory(prefix="deflab_engine_") as tmp:
        path = Path(tmp) / "model.model"
        write_model(isolated, path)
        cmd = [
            str(bin_path),
            str(path),
            "--fragment",
            fragment,
            "--engine",
            engine,
            "--max-depth",
            str(max_depth),
            "--max-k",
            str(max_k),
        ]
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if _NOT_DEFINABLE_RE.search(out):
        definable = False
    elif _DEFINABLE_RE.search(out):
        definable = True
    else:
        raise RuntimeError(f"Rust engine produced no verdict:\n{out}")

    frag_label = f"{fragment}:rust"
    meta = _META_RE.search(out)
    if meta:
        frag_label = meta.group(1)
    return DefinabilityResult(definable=definable, fragment=frag_label)


def prefer_rust_backend() -> bool:
    """Default Rust unless FOPY_ENGINE_BACKEND=python."""
    backend = os.environ.get("FOPY_ENGINE_BACKEND", "auto").strip().lower()
    if backend == "python":
        return False
    if backend == "rust":
        return True
    return is_engine_rust_available()
