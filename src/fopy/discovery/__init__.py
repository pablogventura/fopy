"""Discovery package: automatic sweeps for DefLab."""

from fopy.discovery.sweep import (
    DEFAULT_JOBS,
    JobSpec,
    SweepRecord,
    disagreements,
    run_sweep,
    write_run,
)

__all__ = [
    "DEFAULT_JOBS",
    "JobSpec",
    "SweepRecord",
    "disagreements",
    "run_sweep",
    "write_run",
]
