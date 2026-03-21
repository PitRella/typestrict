"""Rule registry for typeforce.

``RULES`` is the authoritative list of all active rules.  To add a custom
rule, append an instance to this list before running the checker:

    from typeforce.rules import RULES
    from mypackage import MyRule
    RULES.append(MyRule())
"""
from typeforce.rules.base import Rule
from typeforce.rules.classes import ClassAnnotationRule
from typeforce.rules.functions import FunctionAnnotationRule
from typeforce.rules.loops import LoopAnnotationRule
from typeforce.rules.variables import VariableAnnotationRule

RULES: list[Rule] = [
    VariableAnnotationRule(),
    FunctionAnnotationRule(),
    ClassAnnotationRule(),
    LoopAnnotationRule(),
]

__all__ = [
    "Rule",
    "RULES",
    "VariableAnnotationRule",
    "FunctionAnnotationRule",
    "ClassAnnotationRule",
    "LoopAnnotationRule",
]
