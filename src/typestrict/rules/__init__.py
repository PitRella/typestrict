"""Rule registry for typestrict.

``RULES`` is the authoritative list of all active rules.  To add a custom
rule, append an instance to this list before running the checker:

    from typestrict.rules import RULES
    from mypackage import MyRule
    RULES.append(MyRule())
"""
from typestrict.rules.base import Rule
from typestrict.rules.classes import ClassAnnotationRule
from typestrict.rules.functions import FunctionAnnotationRule
from typestrict.rules.loops import LoopAnnotationRule
from typestrict.rules.variables import VariableAnnotationRule

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
