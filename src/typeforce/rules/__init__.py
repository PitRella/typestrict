"""Rule modules for typeforce."""
from typeforce.rules.base import Rule
from typeforce.rules.classes import ClassAnnotationRule
from typeforce.rules.functions import FunctionAnnotationRule
from typeforce.rules.loops import LoopAnnotationRule
from typeforce.rules.variables import VariableAnnotationRule

__all__ = [
    "Rule",
    "VariableAnnotationRule",
    "FunctionAnnotationRule",
    "ClassAnnotationRule",
    "LoopAnnotationRule",
]
