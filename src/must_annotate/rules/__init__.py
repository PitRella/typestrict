"""Rule registry for must-annotate.

``RULES`` is the authoritative list of all active rules.  To add a custom
rule, append an instance to this list before running the checker:

    from must_annotate.rules import RULES
    from mypackage import MyRule
    RULES.append(MyRule())
"""
from must_annotate.rules.base import Rule
from must_annotate.rules.classes import ClassAnnotationRule
from must_annotate.rules.functions import FunctionAnnotationRule
from must_annotate.rules.loops import LoopAnnotationRule
from must_annotate.rules.variables import VariableAnnotationRule

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
