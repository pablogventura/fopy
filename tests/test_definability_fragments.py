"""Fragment support guards."""

import pytest

from fopy.finite import check_definability, explain_definability, normalize_fragment


@pytest.mark.finite
def test_pp_fragment(minimal_model):
    result = check_definability(minimal_model, "T0", fragment="pp")
    assert isinstance(result.definable, bool)
    assert result.fragment == "pp"


@pytest.mark.finite
def test_explain_pp_fragment(minimal_model):
    report = explain_definability(minimal_model, "T0", fragment="pp")
    assert isinstance(report.definable, bool)


@pytest.mark.finite
def test_normalize_horn():
    assert normalize_fragment("horn") == "horn"


@pytest.mark.finite
def test_normalize_unknown():
    with pytest.raises(NotImplementedError):
        normalize_fragment("mso")
