"""OpenDefAlgSplitting (Rust HIT) subprocess backend."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from fopy.finite.hit import Counterexample, HitConfig
from fopy.finite.models import Model
from fopy.finite.open_formulas import Formula, Variable
from fopy.finite.open_parse import parse_open_formula
from fopy.finite.relops import Relation
from fopy.parse.write_model import write_model

HitBackend = Literal["auto", "rust", "python"]

class RustFormulaParseError(RuntimeError):
    """Rust reported DEFINABLE but the witness formula could not be parsed."""

_SUBSCRIPT = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_RUST_BIN_ENV = "FOPY_OPENDEF_BIN"
_RUST_BACKEND_ENV = "FOPY_HIT_BACKEND"

_DEFAULT_BIN_CANDIDATES: tuple[Path, ...] = (
    Path("/home/pablo/mios/adga_tesis/OpenDefAlgSplitting/target/release/opendefalgsplitting"),
    Path("/home/pablo/mios/adga_tesis/OpenDefAlgSplitting/target/debug/opendefalgsplitting"),
)


def find_opendefalgsplitting_binary() -> Path | None:
    """Return the OpenDefAlgSplitting CLI if installed or built locally."""
    override = os.environ.get(_RUST_BIN_ENV)
    if override:
        path = Path(override)
        return path if path.is_file() and os.access(path, os.X_OK) else None
    for candidate in _DEFAULT_BIN_CANDIDATES:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def resolve_hit_backend() -> HitBackend:
    """Resolve the active HIT backend from ``FOPY_HIT_BACKEND``."""
    raw = os.environ.get(_RUST_BACKEND_ENV, "auto").strip().lower()
    if raw in ("rust", "python"):
        return raw  # type: ignore[return-value]
    return "rust" if find_opendefalgsplitting_binary() is not None else "python"


def rust_hit_available() -> bool:
    """Return whether the Rust HIT binary is callable."""
    return find_opendefalgsplitting_binary() is not None


def _normalize_rust_formula(text: str) -> str:
    """Map OpenDefAlgSplitting formula text to ``parse_open_formula`` syntax."""
    s = text.strip()
    if not s:
        raise ValueError("empty formula")
    if s.startswith("⊤") or s.startswith("T("):
        return "true"
    if s.startswith("⊥") or s.startswith("F("):
        return "false"

    s = re.sub(
        r"\bx([₀₁₂₃₄₅₆₇₈₉\d]+)\b",
        lambda m: f"x{m.group(1).translate(_SUBSCRIPT)}",
        s,
    )
    s = s.replace("∧", " & ").replace("∨", " | ")

    def repl_neg_eq(match: re.Match[str]) -> str:
        left, right = match.group(1).strip(), match.group(2).strip()
        return f"(-eq({left}, {right}))"

    s = re.sub(r"¬\s*([^=()&|]+)\s*==\s*([^=()&|]+)", repl_neg_eq, s)
    s = re.sub(r"¬\s*\(", "(-(", s)

    def repl_eq(match: re.Match[str]) -> str:
        left, right = match.group(1).strip(), match.group(2).strip()
        return f"eq({left}, {right})"

    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"([^=!<>&|()]+)\s*==\s*([^=()&|]+)", repl_eq, s)
    return s


def _vars_for_formula(formula_text: str, model: Model) -> dict[str, Variable]:
    indices = {
        int(m.group(1))
        for m in re.finditer(r"\bx(\d+)\b", _normalize_rust_formula(formula_text))
    }
    if not indices:
        indices = {0}
    return {f"x{i}": Variable.from_index(i) for i in sorted(indices)}


def _parse_rust_formula(formula_text: str, model: Model) -> Formula:
    normalized = _normalize_rust_formula(formula_text)
    vars_map = _vars_for_formula(formula_text, model)
    return parse_open_formula(normalized, vars_map, model.operations)


def _parse_rust_output(stdout: str, model: Model) -> Formula | Counterexample:
    if "NOT DEFINABLE" in stdout:
        match = re.search(r"Counterexample:\s*(\[\[.*?\]\])", stdout, re.DOTALL)
        if match is None:
            raise RuntimeError("Rust HIT reported NOT DEFINABLE without counterexample")
        tuples = ast.literal_eval(match.group(1))
        return Counterexample([list(row) for row in tuples])

    if "DEFINABLE" not in stdout:
        raise RuntimeError(f"Unexpected OpenDefAlgSplitting output:\n{stdout}")

    try:
        assign_lines = [line.strip() for line in stdout.splitlines() if ":=" in line]
        if assign_lines:
            _, _, rhs = assign_lines[-1].partition(":=")
            return _parse_rust_formula(rhs.strip(), model)

        by_lines = [line.strip() for line in stdout.splitlines() if line.startswith("by ")]
        if by_lines:
            return _parse_rust_formula(by_lines[-1][3:].strip(), model)
    except ValueError as exc:
        raise RustFormulaParseError("Rust DEFINABLE witness could not be parsed") from exc

    raise RuntimeError(f"Rust HIT reported DEFINABLE without formula:\n{stdout}")


def _model_for_rust(model: Model, targets: list[Relation]) -> Model:
    """Build a model copy whose ``targets`` are the relations under test."""
    relations = {k: v for k, v in model.relations.items() if not k.startswith("T")}
    target_map = {rel.sym: rel for rel in targets}
    for rel in targets:
        relations[rel.sym] = rel
    return Model(
        universe=list(model.universe),
        relations=relations,
        operations=dict(model.operations),
        targets=target_map,
    )


def is_open_def_rust(
    model: Model,
    targets: list[Relation],
    config: HitConfig | None = None,
) -> Formula | Counterexample:
    """Run HIT via the OpenDefAlgSplitting Rust binary."""
    _ = config  # Rust auto-strategy; Python HitConfig knobs are not forwarded yet.
    binary = find_opendefalgsplitting_binary()
    if binary is None:
        raise RuntimeError(
            "OpenDefAlgSplitting binary not found; set FOPY_OPENDEF_BIN or build the crate"
        )

    rust_model = _model_for_rust(model, targets)
    with tempfile.TemporaryDirectory(prefix="fopy-hit-") as tmp:
        model_path = Path(tmp) / "query.model"
        write_model(rust_model, model_path)
        proc = subprocess.run(
            [str(binary), str(model_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if proc.returncode != 0 and "DEFINABLE" not in stdout and "NOT DEFINABLE" not in stdout:
        raise RuntimeError(
            f"OpenDefAlgSplitting failed (exit {proc.returncode}):\n{stdout}\n{stderr}"
        )
    return _parse_rust_output(stdout, model)
