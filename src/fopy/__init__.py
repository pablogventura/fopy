"""
fopy — symbolic first-order logic for Python.

Import as ``import fopy as fo`` or ``from fopy import ...``.

>>> import fopy as fo
>>> x, y = fo.symbols("x y")
>>> fo.latex(fo.eq(x, y))
'x = y'
"""

from __future__ import annotations

__version__ = "0.1.0"

from fopy import builders, finite
from fopy.bridge import from_finite_model, load_structure, to_finite_model
from fopy.core.visitor import Visitor
from fopy.formulas import (
    And,
    Atom,
    Eq,
    Exists,
    FalseF,
    ForAll,
    Formula,
    Not,
    Or,
    TrueF,
    exists,
    forall,
)
from fopy.parse import parse_formula, parse_model
from fopy.printing import latex, pprint, sstr
from fopy.semantics import evaluate, extension, satisfy
from fopy.signature import Signature
from fopy.simplify import and_formula, eq, false_formula, neg, or_formula, simplify, true_formula
from fopy.structures import Structure
from fopy.symbols import ConstantSymbol, FuncSymbol, RelSymbol, Variable, symbols
from fopy.terms import Apply, Constant, Term
from fopy.theories import Theory
from fopy.transform import bound_vars, free_vars, rename_bound, subs, substitute

__all__ = [
    "And",
    "Apply",
    "Atom",
    "Constant",
    "ConstantSymbol",
    "Eq",
    "Exists",
    "FalseF",
    "ForAll",
    "Formula",
    "FuncSymbol",
    "Not",
    "Or",
    "RelSymbol",
    "Signature",
    "Structure",
    "Term",
    "Theory",
    "TrueF",
    "Variable",
    "Visitor",
    "and_formula",
    "bound_vars",
    "builders",
    "eq",
    "evaluate",
    "exists",
    "extension",
    "false_formula",
    "finite",
    "forall",
    "free_vars",
    "from_finite_model",
    "latex",
    "load_structure",
    "neg",
    "or_formula",
    "parse_formula",
    "parse_model",
    "pprint",
    "rename_bound",
    "satisfy",
    "simplify",
    "sstr",
    "subs",
    "substitute",
    "symbols",
    "to_finite_model",
    "true_formula",
    "__version__",
]

try:
    from fopy import draw as draw  # noqa: F401

    __all__.append("draw")
except ImportError:
    draw = None  # type: ignore[assignment,misc]
