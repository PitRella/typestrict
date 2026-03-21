"""TF004 – class attribute assignments without type annotations."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError

_RULE_CODE: str = "TF004"


def _get_self_name(init_node: ast.FunctionDef) -> str | None:
    """Return the name of the first argument (``self``) or None."""
    if init_node.args.args:
        return init_node.args.args[0].arg
    return None


def _check_init_body(
    init_node: ast.FunctionDef,
    filename: str,
) -> list[TypeforceError]:
    """Check ``self.attr = value`` patterns in ``__init__``."""
    errors: list[TypeforceError] = []
    self_name: str | None = _get_self_name(init_node)
    if self_name is None:
        return errors

    for stmt in ast.walk(init_node):
        if not isinstance(stmt, ast.Assign):
            continue
        for target in stmt.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == self_name
            ):
                errors.append(
                    TypeforceError(
                        file=filename,
                        line=stmt.lineno,
                        col=stmt.col_offset,
                        code=_RULE_CODE,
                        message=(
                            f"Attribute '{self_name}.{target.attr}' "
                            "missing type annotation"
                        ),
                    )
                )
    return errors


def _check_class_body(
    class_node: ast.ClassDef,
    filename: str,
) -> list[TypeforceError]:
    """Check class-level ``ast.Assign`` statements (not inside methods)."""
    errors: list[TypeforceError] = []

    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            # Class-level plain assignment – TF004
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    errors.append(
                        TypeforceError(
                            file=filename,
                            line=stmt.lineno,
                            col=stmt.col_offset,
                            code=_RULE_CODE,
                            message=(
                                f"Class attribute '{target.id}' missing type annotation"
                            ),
                        )
                    )
    return errors


def check_class(
    node: ast.ClassDef,
    filename: str,
) -> list[TypeforceError]:
    """Check a class definition for TF004 violations."""
    errors: list[TypeforceError] = []

    errors.extend(_check_class_body(node, filename))

    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
            errors.extend(_check_init_body(stmt, filename))

    return errors
