"""Finite structures, open formulas, and HIT definability."""

from fopy.finite.definability import DefinabilityResult, is_open_definable
from fopy.finite.hit import (
    Block,
    Counterexample,
    HitConfig,
    IndicesTupleGenerator,
    TupleHistory,
    information_gain_from_counts,
    is_open_def,
)
from fopy.finite.models import Model
from fopy.finite.open_formulas import (
    Formula,
    OpSym,
    Term,
    Variable,
    and_formula,
    eq,
    extension,
    false_formula,
    neg,
    or_formula,
    satisfy,
    true_formula,
    variables,
)
from fopy.finite.preprocessing import Pattern, preprocesamiento2, split_targets
from fopy.finite.relops import Operation, Relation

__all__ = [
    "Block",
    "Counterexample",
    "DefinabilityResult",
    "Formula",
    "HitConfig",
    "IndicesTupleGenerator",
    "Model",
    "Operation",
    "OpSym",
    "Pattern",
    "Relation",
    "Term",
    "TupleHistory",
    "Variable",
    "and_formula",
    "eq",
    "extension",
    "false_formula",
    "information_gain_from_counts",
    "is_open_def",
    "is_open_definable",
    "neg",
    "or_formula",
    "preprocesamiento2",
    "satisfy",
    "split_targets",
    "true_formula",
    "variables",
]
