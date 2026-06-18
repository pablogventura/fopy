"""Optional Z3 solver backend."""

import pytest

from fopy.solvers import check_sat_smt, z3_available


@pytest.mark.solvers
def test_z3_sat():
    if not z3_available():
        pytest.skip("z3 not installed")
    result = check_sat_smt("(assert true)")
    assert result == "sat"


def test_z3_missing_graceful():
    if z3_available():
        pytest.skip("z3 installed")
    assert check_sat_smt("(assert true)") is None
