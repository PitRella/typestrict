"""TF005 – loop/context-manager variables without type annotations.

This rule is **disabled by default**.  Enable it via ``strict = true`` or by
removing ``TF005`` from the ``ignore`` list in ``[tool.typeforce]``.
"""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError

_RULE_CODE: str = "TF005"


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


def check_loop(node: ast.For, filename: str) -> list[TypeforceError]:
    """Check ``for <target> in …`` for TF005 violations.

    Because Python's ``for`` loop syntax does not support inline annotations
    (``for x: int in …`` is a SyntaxError), every loop variable is flagged.
    The rule is opt-in for teams that use the ``# type: …`` comment convention.
    """
    errors: list[TypeforceError] = []

    for name in _target_names(node.target):
        if name == "_":
            continue
        errors.append(
            TypeforceError(
                file=filename,
                line=node.lineno,
                col=node.col_offset,
                code=_RULE_CODE,
                message=f"Loop variable '{name}' missing type annotation",
            )
        )

    return errors


def check_with(node: ast.With, filename: str) -> list[TypeforceError]:
    """Check ``with … as <target>`` for TF005 violations."""
    errors: list[TypeforceError] = []

    for item in node.items:
        if item.optional_vars is None:
            continue
        for name in _target_names(item.optional_vars):
            if name == "_":
                continue
            errors.append(
                TypeforceError(
                    file=filename,
                    line=node.lineno,
                    col=node.col_offset,
                    code=_RULE_CODE,
                    message=f"Context variable '{name}' missing type annotation",
                )
            )

    return errors
