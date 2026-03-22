"""TF005 – loop/context-manager variables without type annotations.

This rule is **disabled by default**.  Enable it via ``strict = true`` or by
removing ``TF005`` from the ``ignore`` list in ``[tool.must-annotate]``.
"""
from __future__ import annotations

import ast
from typing import ClassVar

from must_annotate.errors import MustAnnotateError
from must_annotate.rules.base import Rule


def _target_names(target: ast.expr) -> list[str]:
    """Collect variable names from a for-loop or with-statement target."""
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in target.elts:
            names.extend(_target_names(elt))
        return names
    return []


class LoopAnnotationRule(Rule):
    """TF005 – loop and context-manager variable without type annotation."""

    code: ClassVar[str] = "TF005"
    node_types: ClassVar[tuple[type[ast.AST], ...]] = (
        ast.For, ast.AsyncFor, ast.With, ast.AsyncWith
    )

    def check(self, node: ast.AST, filename: str) -> list[MustAnnotateError]:
        assert isinstance(node, (ast.For, ast.AsyncFor, ast.With, ast.AsyncWith))
        if isinstance(node, (ast.For, ast.AsyncFor)):
            return self._check_for(node, filename)
        return self._check_with(node, filename)

    def _check_for(self, node: ast.For | ast.AsyncFor, filename: str) -> list[MustAnnotateError]:
        """Check ``for <target> in …`` for TF005 violations.

        Because Python's ``for`` loop syntax does not support inline
        annotations (``for x: int in …`` is a SyntaxError), every loop
        variable is flagged. The rule is opt-in for teams that use the
        ``# type: …`` comment convention.
        """
        errors: list[MustAnnotateError] = []
        for name in _target_names(node.target):
            if name == "_":
                continue
            errors.append(
                MustAnnotateError(
                    file=filename,
                    line=node.lineno,
                    col=node.col_offset,
                    code=self.code,
                    message=f"Loop variable '{name}' missing type annotation",
                )
            )
        return errors

    def _check_with(self, node: ast.With | ast.AsyncWith, filename: str) -> list[MustAnnotateError]:
        """Check ``with … as <target>`` for TF005 violations."""
        errors: list[MustAnnotateError] = []
        for item in node.items:
            if item.optional_vars is None:
                continue
            for name in _target_names(item.optional_vars):
                if name == "_":
                    continue
                errors.append(
                    MustAnnotateError(
                        file=filename,
                        line=node.lineno,
                        col=node.col_offset,
                        code=self.code,
                        message=f"Context variable '{name}' missing type annotation",
                    )
                )
        return errors
