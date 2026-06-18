"""Printing for finite open formulas."""

from __future__ import annotations

from fopy.finite.explain import format_open_formula, latex_open_formula
from fopy.finite.open_formulas import Formula


def sstr(formula: Formula) -> str:
    """String form compatible with :mod:`fopy.finite.open_parse`."""
    return format_open_formula(formula)


def latex(formula: Formula) -> str:
    """LaTeX for an open formula."""
    return latex_open_formula(formula)
