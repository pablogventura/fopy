"""Optional Z3 backend (requires z3-solver)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fopy.formulas import Formula


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


def prove_formula(phi: Formula) -> bool | None:
    """Attempt to prove *phi* valid using Z3 (returns ``None`` without Z3).

    Treats *phi* as a closed sentence and checks unsatisfiability of ``¬phi``.

    Args:
        phi: Symbolic first-order formula.

    Returns:
        ``True`` if Z3 reports ``unsat`` for the negation, ``False`` if ``sat``,
        ``None`` when Z3 is unavailable or translation fails.
    """
    from fopy.solvers.z3_formula import formula_to_z3

    if not z3_available():
        return None
    import z3

    expr = formula_to_z3(phi)
    if expr is None:
        return None
    solver = z3.Solver()
    solver.add(z3.Not(expr))
    result = solver.check()
    if result == z3.unsat:
        return True
    if result == z3.sat:
        return False
    return None
