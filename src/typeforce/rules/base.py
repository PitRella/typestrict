"""Abstract base class for all typeforce rules."""
from __future__ import annotations

import ast
from abc import ABC, abstractmethod

from typeforce.errors import TypeforceError


class Rule(ABC):
    """Base class for a single typeforce rule.

    Subclasses must declare:
    - ``code``       – the rule code, e.g. ``"TF001"``
    - ``node_types`` – AST node types this rule handles

    The checker builds a dispatch table from ``node_types`` so new rules are
    picked up automatically without touching ``checker.py``.
    """

    code: str
    node_types: tuple[type[ast.AST], ...]

    @abstractmethod
    def check(self, node: ast.AST, filename: str) -> list[TypeforceError]:
        """Check *node* and return any violations found."""
