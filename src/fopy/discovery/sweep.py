"""Automatic DefLab discovery sweeps (JSONL + disagreement report)."""

from __future__ import annotations

import gc
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence, TextIO

from fopy.finite.definability import check_definability
from fopy.finite.lindenbaum import chain_product_lattice, parse_grid_name
from fopy.finite.models import Model
from fopy.finite.relops import Relation
from fopy.parse import parse_model

# Stems with |U|<=5 only (test2/u100, msimple/u8, etc. excluded on purpose).
SMALL_MODEL_STEMS: frozenset[str] = frozenset(
    {
        "minimal",
        "universo_un_elemento",
        "target_vacio",
        "modelo_solo_target",
        "modeloqueanda",
        "retrombo",
        "retrombo2",
        "retrombo3",
        "retrombo_nodef",
        "retrombo_nodef_sinpura",
        "retrombo_incomparables",
        "retrombo_incomparables_iguales",
        "retromboconstantes",
        "retromboconformula",
        "posetrombo",
        "romboconinfimo",
        "romboletras",
        "cadena4",
        "cadena5",
        "suma4",
        "algebra",
        "malvada",
        "miprueba",
        "unary_singleton",
        "unary_empty_noops",
        "unary_full_noops",
        "unary_partial_noops",
        "unary_flip_partial",
        "unary_cycle3_partial",
    }
)

# Default: only 2x2. Larger grids (3x2 |U|=6) need --grids and eat RAM via rayon.
DEFAULT_GRIDS: tuple[str, ...] = ("2x2",)

# Hard RAM guards: |U|=100 arity-1 used to pass the old power check and blow memory.
MAX_UNIVERSE_SIZE: int = 5
MAX_UNIVERSE_POWER: int = 64
MAX_MORPH_UNIVERSE: int = 4
# fo/horn Python fallback (and heavy Rust) explode past this.
MAX_HEAVY_FRAGMENT_POWER: int = 16
MIN_MEM_AVAILABLE_GIB: float = 4.0
DEFAULT_RAYON_THREADS: int = 2
DEFAULT_JOB_TIMEOUT_S: float = 20.0

HEAVY_FRAGMENTS: frozenset[str] = frozenset({"fo"})



@dataclass(frozen=True)
class JobSpec:
    """One (fragment, engine) pair for the sweep."""

    fragment: str
    engine: str = "auto"
    max_depth: int = 2
    max_k: int = 1


DEFAULT_JOBS: tuple[JobSpec, ...] = (
    JobSpec("qf", "hit"),
    JobSpec("qf", "merge"),
    JobSpec("qf_pos", "split"),
    JobSpec("ep", "split"),
    JobSpec("ep", "ktypes"),
    JobSpec("ex", "split"),
    JobSpec("pp", "split", max_depth=2),
    JobSpec("atomic_conj", "split", max_depth=1),
    JobSpec("gf", "split", max_k=1),
    JobSpec("fo", "split", max_k=1),
    JobSpec("horn", "split"),
)


@dataclass
class SweepRecord:
    """One JSONL row: model x target x fragment/engine verdict."""

    model: str
    model_kind: str
    universe_size: int
    target: str
    target_arity: int
    fragment: str
    engine: str
    definable: bool | None
    elapsed_ms: float
    backend: str | None = None
    error: str | None = None
    skipped: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


@dataclass
class LoadedModel:
    """Model plus display key and source kind."""

    key: str
    kind: str
    model: Model
    path: Path | None = None


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "fopy").is_dir() and (parent / "OpenDefAlgSplitting").is_dir():
            return parent
    # Fallback: fopy/src/fopy/discovery/sweep.py -> adga_tesis
    return here.parents[4]


def default_model_dirs() -> list[Path]:
    root = _repo_root()
    return [
        root / "fopy" / "tests" / "fixtures" / "models",
        root / "OpenDefAlgSplitting" / "model_examples",
    ]


def default_runs_dir() -> Path:
    return _repo_root() / "fopy" / "discovery" / "runs"


def _available_mem_gib() -> float | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    kib = int(line.split()[1])
                    return kib / (1024 * 1024)
    except OSError:
        return None
    return None


def synthetic_targets(model: Model) -> dict[str, Relation]:
    """Build diag / empty / full / le (meet-order) when the model has no T*."""
    u = list(model.universe)
    n = len(u)
    out: dict[str, Relation] = {}
    out["T_diag"] = Relation.new("T_diag", 2).with_tuples([(x, x) for x in u])
    out["T_empty"] = Relation.new("T_empty", 2)
    out["T_full"] = Relation.new("T_full", 2).with_tuples(
        [(x, y) for x in u for y in u]
    )
    meet = model.operations.get("meet")
    if meet is not None and meet.arity == 2:
        le_tuples: list[tuple[int, int]] = []
        for x in u:
            for y in u:
                m = meet.call((x, y))
                if m is not None and m == x:
                    le_tuples.append((x, y))
        out["T_le"] = Relation.new("T_le", 2).with_tuples(le_tuples)
    elif n <= 8:
        # Fallback: discrete order (equality only) already covered by diag;
        # add a simple "first half" unary for variety on non-lattices.
        half = u[: max(1, n // 2)]
        out["T_half"] = Relation.new("T_half", 1).with_tuples([(x,) for x in half])
    return out


def iter_targets(model: Model) -> Iterator[tuple[str, Relation]]:
    """Yield named targets: model T* first, else synthetics."""
    if model.targets:
        for sym, rel in sorted(model.targets.items()):
            yield sym, rel
        return
    for sym, rel in sorted(synthetic_targets(model).items()):
        yield sym, rel


def _should_skip_job(
    model: Model,
    target: Relation,
    job: JobSpec,
    *,
    allow_large_morph: bool,
    max_universe: int = MAX_UNIVERSE_SIZE,
) -> str | None:
    n = len(model.universe)
    if n > max_universe:
        return f"|U|={n}>{max_universe}"
    arity = max(target.arity, 0)
    power = n**arity if arity else n
    if power > MAX_UNIVERSE_POWER:
        return f"|U|^arity={power}>{MAX_UNIVERSE_POWER}"
    if job.fragment in HEAVY_FRAGMENTS and power > MAX_HEAVY_FRAGMENT_POWER:
        return f"heavy {job.fragment} |U|^arity={power}>{MAX_HEAVY_FRAGMENT_POWER}"
    avail = _available_mem_gib()
    if avail is not None and avail < MIN_MEM_AVAILABLE_GIB:
        return f"low MemAvailable={avail:.1f}GiB"
    morph_frags = {"ep", "ex"}
    if job.fragment in morph_frags or (
        job.fragment == "qf" and job.engine == "merge"
    ):
        if n > MAX_MORPH_UNIVERSE and not allow_large_morph:
            return f"morph/merge |U|={n}>{MAX_MORPH_UNIVERSE}"
    return None


class _JobTimeout(Exception):
    """Raised when a sweep cell exceeds its wall-clock budget."""


def _run_with_timeout(fn, timeout_s: float):
    """Run *fn* under SIGALRM; only safe from the main thread."""
    import signal

    if timeout_s <= 0:
        return fn()

    def _handler(_signum, _frame):  # noqa: ANN001
        raise _JobTimeout(f"timeout after {timeout_s}s")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


def load_grid(name: str) -> LoadedModel:
    w, h = parse_grid_name(name)
    return LoadedModel(key=f"C{w}x{h}", kind="grid", model=chain_product_lattice(w, h))


def load_model_file(path: Path) -> LoadedModel:
    model = parse_model(str(path), preprocess=True)
    return LoadedModel(key=path.stem, kind="file", model=model, path=path)


def collect_models(
    *,
    grids: Sequence[str] = DEFAULT_GRIDS,
    model_dirs: Sequence[Path] | None = None,
    stems: frozenset[str] | None = SMALL_MODEL_STEMS,
    extra_paths: Sequence[Path] = (),
    max_universe: int = MAX_UNIVERSE_SIZE,
) -> list[LoadedModel]:
    """Load grids + filtered ``.model`` files (dedupe by stem, first wins)."""
    loaded: list[LoadedModel] = []
    seen: set[str] = set()

    for g in grids:
        lm = load_grid(g)
        if len(lm.model.universe) > max_universe:
            continue
        if lm.key not in seen:
            seen.add(lm.key)
            loaded.append(lm)

    dirs = list(model_dirs) if model_dirs is not None else default_model_dirs()
    paths: list[Path] = []
    for d in dirs:
        if d.is_dir():
            paths.extend(sorted(d.glob("*.model")))
    paths.extend(extra_paths)

    allow = stems
    for path in paths:
        stem = path.stem
        if allow is not None and stem not in allow:
            continue
        if stem in seen:
            continue
        try:
            lm = load_model_file(path)
        except Exception:
            continue
        if len(lm.model.universe) > max_universe:
            continue
        seen.add(stem)
        loaded.append(lm)
    return loaded


def run_one(
    loaded: LoadedModel,
    target_sym: str,
    target: Relation,
    job: JobSpec,
    *,
    allow_large_morph: bool = False,
    max_universe: int = MAX_UNIVERSE_SIZE,
    timeout_s: float = DEFAULT_JOB_TIMEOUT_S,
) -> SweepRecord:
    """Evaluate one job; never raises (errors become record fields)."""
    skip = _should_skip_job(
        loaded.model,
        target,
        job,
        allow_large_morph=allow_large_morph,
        max_universe=max_universe,
    )
    base = SweepRecord(
        model=loaded.key,
        model_kind=loaded.kind,
        universe_size=len(loaded.model.universe),
        target=target_sym,
        target_arity=target.arity,
        fragment=job.fragment,
        engine=job.engine,
        definable=None,
        elapsed_ms=0.0,
        skipped=skip,
    )
    if skip:
        return base

    t0 = time.perf_counter()
    try:
        # Prefer Rust only during sweep; avoid silent Python fallback hang.
        prev_backend = os.environ.get("FOPY_ENGINE_BACKEND")
        prev_hit_to = os.environ.get("FOPY_HIT_TIMEOUT_S")
        os.environ["FOPY_ENGINE_BACKEND"] = "rust"
        os.environ.setdefault("FOPY_SKIP_WITNESS", "1")
        if timeout_s > 0:
            os.environ["FOPY_HIT_TIMEOUT_S"] = str(timeout_s)

        def _call():
            return check_definability(
                loaded.model,
                target,
                fragment=job.fragment,
                engine=job.engine,
                max_depth=job.max_depth,
                max_k=job.max_k,
                timeout_s=timeout_s if timeout_s > 0 else 120.0,
            )

        try:
            result = _run_with_timeout(_call, timeout_s)
        finally:
            if prev_backend is None:
                os.environ.pop("FOPY_ENGINE_BACKEND", None)
            else:
                os.environ["FOPY_ENGINE_BACKEND"] = prev_backend
            if prev_hit_to is None:
                os.environ.pop("FOPY_HIT_TIMEOUT_S", None)
            else:
                os.environ["FOPY_HIT_TIMEOUT_S"] = prev_hit_to

        elapsed = (time.perf_counter() - t0) * 1000.0
        return SweepRecord(
            model=loaded.key,
            model_kind=loaded.kind,
            universe_size=len(loaded.model.universe),
            target=target_sym,
            target_arity=target.arity,
            fragment=job.fragment,
            engine=job.engine,
            definable=result.definable,
            elapsed_ms=round(elapsed, 3),
            backend=result.fragment,
        )
    except Exception as exc:  # noqa: BLE001 - sweep must not abort
        elapsed = (time.perf_counter() - t0) * 1000.0
        return SweepRecord(
            model=loaded.key,
            model_kind=loaded.kind,
            universe_size=len(loaded.model.universe),
            target=target_sym,
            target_arity=target.arity,
            fragment=job.fragment,
            engine=job.engine,
            definable=None,
            elapsed_ms=round(elapsed, 3),
            error=f"{type(exc).__name__}: {exc}",
        )


def _limit_rayon_threads(n: int = DEFAULT_RAYON_THREADS) -> None:
    """Cap Rust rayon parallelism before spawning engine subprocesses."""
    os.environ.setdefault("RAYON_NUM_THREADS", str(max(1, n)))


def run_sweep(
    *,
    grids: Sequence[str] = DEFAULT_GRIDS,
    model_dirs: Sequence[Path] | None = None,
    stems: frozenset[str] | None = SMALL_MODEL_STEMS,
    jobs: Sequence[JobSpec] = DEFAULT_JOBS,
    allow_large_morph: bool = False,
    max_models: int | None = None,
    max_universe: int = MAX_UNIVERSE_SIZE,
    rayon_threads: int = DEFAULT_RAYON_THREADS,
    job_timeout_s: float = DEFAULT_JOB_TIMEOUT_S,
    jsonl_fh: TextIO | None = None,
) -> list[SweepRecord]:
    """Run the full cartesian product of models x targets x jobs.

    Memory policy: drop models with ``|U| > max_universe``, cap rayon threads,
    skip when MemAvailable is low, per-job wall timeout, and optionally stream
    JSONL as rows finish.
    """
    _limit_rayon_threads(rayon_threads)
    models = collect_models(
        grids=grids,
        model_dirs=model_dirs,
        stems=stems,
        max_universe=max_universe,
    )
    if max_models is not None:
        models = models[:max_models]
    records: list[SweepRecord] = []
    done = 0
    for loaded in models:
        for t_sym, t_rel in iter_targets(loaded.model):
            for job in jobs:
                rec = run_one(
                    loaded,
                    t_sym,
                    t_rel,
                    job,
                    allow_large_morph=allow_large_morph,
                    max_universe=max_universe,
                    timeout_s=job_timeout_s,
                )
                records.append(rec)
                if jsonl_fh is not None:
                    jsonl_fh.write(rec.to_json() + "\n")
                    jsonl_fh.flush()
                done += 1
                if done % 20 == 0:
                    gc.collect()
        gc.collect()
    return records


def disagreements(records: Iterable[SweepRecord]) -> list[dict]:
    """Group by (model, target) and list fragment/engine pairs that disagree."""
    groups: dict[tuple[str, str], list[SweepRecord]] = {}
    for rec in records:
        if rec.skipped or rec.error or rec.definable is None:
            continue
        groups.setdefault((rec.model, rec.target), []).append(rec)

    out: list[dict] = []
    for (model, target), rows in sorted(groups.items()):
        verdicts: dict[bool, list[str]] = {True: [], False: []}
        for r in rows:
            assert r.definable is not None
            label = f"{r.fragment}/{r.engine}"
            verdicts[r.definable].append(label)
        if verdicts[True] and verdicts[False]:
            out.append(
                {
                    "model": model,
                    "target": target,
                    "definable_yes": sorted(set(verdicts[True])),
                    "definable_no": sorted(set(verdicts[False])),
                }
            )
    return out


def error_summary(records: Iterable[SweepRecord]) -> list[dict]:
    """Compact list of errored or skipped cells."""
    rows: list[dict] = []
    for r in records:
        if r.error:
            rows.append(
                {
                    "model": r.model,
                    "target": r.target,
                    "fragment": r.fragment,
                    "engine": r.engine,
                    "error": r.error,
                }
            )
    return rows


def write_run(
    records: Sequence[SweepRecord],
    *,
    runs_dir: Path | None = None,
    tag: str | None = None,
    jsonl_already_written: bool = False,
) -> tuple[Path, Path]:
    """Write JSONL + summary JSON; return ``(jsonl_path, summary_path)``."""
    out_dir = runs_dir or default_runs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = tag or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    jsonl_path = out_dir / f"{stamp}.jsonl"
    summary_path = out_dir / f"{stamp}_summary.json"

    if not jsonl_already_written:
        with jsonl_path.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(rec.to_json() + "\n")

    decided = [r for r in records if r.definable is not None and not r.skipped]
    summary = {
        "stamp": stamp,
        "total_rows": len(records),
        "decided": len(decided),
        "skipped": sum(1 for r in records if r.skipped),
        "errors": sum(1 for r in records if r.error),
        "definable_true": sum(1 for r in decided if r.definable),
        "definable_false": sum(1 for r in decided if not r.definable),
        "disagreements": disagreements(records),
        "error_samples": error_summary(records)[:40],
        "backend": os.environ.get("FOPY_ENGINE_BACKEND", "auto"),
        "rayon_num_threads": os.environ.get("RAYON_NUM_THREADS"),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return jsonl_path, summary_path
