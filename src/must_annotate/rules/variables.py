"""TF001 – variable assignment without a type annotation."""
from __future__ import annotations

import ast
from typing import ClassVar

from must_annotate.errors import MustAnnotateError
from must_annotate.rules.base import Rule

_DUNDER_PREFIX: str = "__"


def _is_dunder_name(name: str) -> bool:
    return name.startswith(_DUNDER_PREFIX) and name.endswith(_DUNDER_PREFIX)


def _collect_names(target: ast.expr) -> list[str]:
    """Recursively collect variable names from an assignment target.

    Handles simple names (``x``), tuple/list unpacking (``a, b = …``),
    nested unpacking (``(a, (b, c)) = …``), and starred targets
    (``a, *rest, c = …``).
    Attribute targets (``obj.attr``) are ignored – handled by TF004.
    """
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Starred):
        return _collect_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in target.elts:
            names.extend(_collect_names(elt))
        return names
    return []


class VariableAnnotationRule(Rule):
    """TF001 – plain variable assignment without annotation."""

    code: ClassVar[str] = "TF001"
    node_types: ClassVar[tuple[type[ast.AST], ...]] = (ast.Assign,)
    skip_in_class_body: ClassVar[bool] = True

    def check(self, node: ast.AST, filename: str) -> list[MustAnnotateError]:
        assert isinstance(node, ast.Assign)
        errors: list[MustAnnotateError] = []

        for target in node.targets:
            for name in _collect_names(target):
                if name == "_" or _is_dunder_name(name):
                    continue
                errors.append(
                    MustAnnotateError(
                        file=filename,
                        line=node.lineno,
                        col=node.col_offset,
                        code=self.code,
                        message=f"Variable '{name}' missing type annotation",
                    )
                )

        return errors
