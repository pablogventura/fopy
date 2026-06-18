"""Optional Z3 backend (requires z3-solver)."""

from __future__ import annotations


def z3_available() -> bool:
    """Return ``True`` when the optional ``z3-solver`` package is importable."""
    try:
        import z3  # noqa: F401

        return True
    except ImportError:
        return False


def check_sat_smt(smtlib: str) -> str | None:
    """Run Z3 on an SMT-LIB string.

    Args:
        smtlib: Full SMT-LIB script (assertions and check-sat).

    Returns:
        ``"sat"``, ``"unsat"``, or ``"unknown"`` when Z3 is available;
        ``None`` when the Z3 backend is not installed.
    """
    if not z3_available():
        return None
    import z3

    solver = z3.Solver()
    solver.from_string(smtlib)
    result = solver.check()
    return str(result)
