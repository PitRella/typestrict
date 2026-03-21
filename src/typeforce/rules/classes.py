"""TF004 – class attribute assignments without type annotations."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError
from typeforce.rules.base import Rule


def _get_self_name(init_node: ast.FunctionDef) -> str | None:
    """Return the name of the first argument (``self``) or None."""
    if init_node.args.args:
        return init_node.args.args[0].arg
    return None


class ClassAnnotationRule(Rule):
    """TF004 – class attribute assignments without type annotations."""

    code = "TF004"
    node_types = (ast.ClassDef,)

    def check(self, node: ast.AST, filename: str) -> list[TypeforceError]:
        assert isinstance(node, ast.ClassDef)
        errors: list[TypeforceError] = []

        errors.extend(self._check_class_body(node, filename))

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                errors.extend(self._check_init_body(stmt, filename))

        return errors

    def _check_class_body(
        self,
        class_node: ast.ClassDef,
        filename: str,
    ) -> list[TypeforceError]:
        """Check class-level ``ast.Assign`` statements (not inside methods)."""
        errors: list[TypeforceError] = []

        for stmt in class_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        errors.append(
                            TypeforceError(
                                file=filename,
                                line=stmt.lineno,
                                col=stmt.col_offset,
                                code=self.code,
                                message=f"Class attribute '{target.id}' missing type annotation",
                            )
                        )
        return errors

    def _check_init_body(
        self,
        init_node: ast.FunctionDef,
        filename: str,
    ) -> list[TypeforceError]:
        """Check ``self.attr = value`` patterns in ``__init__``."""
        errors: list[TypeforceError] = []
        self_name = _get_self_name(init_node)
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
                            code=self.code,
                            message=(
                                f"Attribute '{self_name}.{target.attr}' "
                                "missing type annotation"
                            ),
                        )
                    )
        return errors
