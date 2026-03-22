"""Abstract base class for all typestrict rules."""
from __future__ import annotations

import ast
from abc import ABC, abstractmethod
from typing import ClassVar

from typestrict.errors import TypestrictError


class Rule(ABC):
    """Base class for a single typestrict rule.

    Subclasses must declare:
    - ``code``       – the rule code, e.g. ``"TF001"``
    - ``node_types`` – AST node types this rule handles

    Optional overrides:
    - ``skip_in_class_body`` – set to ``True`` to skip nodes that appear
      directly inside a class body (default: ``False``)

    The checker builds a dispatch table from ``node_types`` automatically,
    so new rules are picked up without touching ``checker.py``.
    """

    code: ClassVar[str]
    node_types: ClassVar[tuple[type[ast.AST], ...]]
    skip_in_class_body: ClassVar[bool] = False

    @abstractmethod
    def check(self, node: ast.AST, filename: str) -> list[TypestrictError]:
        """Check *node* and return any violations found."""
