"""TF001 – variable assignment without a type annotation."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError
from typeforce.rules.base import Rule

_DUNDER_PREFIX: str = "__"


def _is_dunder_name(name: str) -> bool:
    return name.startswith(_DUNDER_PREFIX) and name.endswith(_DUNDER_PREFIX)


def _collect_names(target: ast.expr) -> list[str]:
    """Recursively collect variable names from an assignment target.

    Handles simple names (``x``), tuple/list unpacking (``a, b = …``),
    and nested unpacking (``(a, (b, c)) = …``).
    Attribute targets (``obj.attr``) are ignored – handled by TF004.
    """
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in target.elts:
            names.extend(_collect_names(elt))
        return names
    return []


class VariableAnnotationRule(Rule):
    """TF001 – plain variable assignment without annotation."""

    code = "TF001"
    node_types = (ast.Assign,)

    def check(self, node: ast.AST, filename: str) -> list[TypeforceError]:
        assert isinstance(node, ast.Assign)
        errors: list[TypeforceError] = []

        for target in node.targets:
            for name in _collect_names(target):
                if name == "_" or _is_dunder_name(name):
                    continue
                errors.append(
                    TypeforceError(
                        file=filename,
                        line=node.lineno,
                        col=node.col_offset,
                        code=self.code,
                        message=f"Variable '{name}' missing type annotation",
                    )
                )

        return errors
