"""Smoke tests for discovery sweep helpers."""

from __future__ import annotations

from fopy.discovery.sweep import (
    DEFAULT_JOBS,
    JobSpec,
    disagreements,
    run_sweep,
    synthetic_targets,
    write_run,
)
from fopy.finite.lindenbaum import chain_product_lattice


def test_synthetic_targets_on_2x2():
    model = chain_product_lattice(2, 2)
    targets = synthetic_targets(model)
    assert "T_diag" in targets
    assert "T_empty" in targets
    assert "T_full" in targets
    assert "T_le" in targets
    assert targets["T_diag"].arity == 2
    assert len(targets["T_diag"].r) == len(model.universe)


def test_mini_sweep_writes_jsonl(tmp_path):
    records = run_sweep(
        grids=("2x2",),
        stems=frozenset(),  # grids only
        jobs=(JobSpec("qf", "hit"), JobSpec("qf_pos", "split")),
        max_models=1,
    )
    assert records
    assert any(r.definable is not None or r.skipped or r.error for r in records)
    jsonl, summary = write_run(records, runs_dir=tmp_path, tag="test_mini")
    assert jsonl.is_file()
    assert summary.is_file()
    text = jsonl.read_text(encoding="utf-8")
    assert "T_diag" in text or "qf" in text
    _ = disagreements(records)
    assert DEFAULT_JOBS
