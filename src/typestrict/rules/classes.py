"""TF004 – class attribute assignments without type annotations."""
from __future__ import annotations

import ast
from collections.abc import Iterator
from typing import ClassVar

from typestrict.errors import TypestrictError
from typestrict.rules.base import Rule

# Node types that introduce a new scope — we stop descending into these.
_SCOPE_NODES: tuple[type[ast.AST], ...] = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
)


def _get_self_name(init_node: ast.FunctionDef) -> str | None:
    """Return the name of the first argument (``self``) or None."""
    if init_node.args.args:
        return init_node.args.args[0].arg
    return None


def _walk_no_nested_scopes(node: ast.AST) -> Iterator[ast.AST]:
    """Yield descendant nodes, but do not descend into nested scopes.

    Unlike ``ast.walk()``, this stops at ``FunctionDef``, ``AsyncFunctionDef``,
    and ``ClassDef`` so that assignments inside nested functions are not
    mistakenly attributed to the outer ``__init__``.
    """
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _SCOPE_NODES):
            continue
        yield from _walk_no_nested_scopes(child)


class ClassAnnotationRule(Rule):
    """TF004 – class attribute assignments without type annotations."""

    code: ClassVar[str] = "TF004"
    node_types: ClassVar[tuple[type[ast.AST], ...]] = (ast.ClassDef,)

    def check(self, node: ast.AST, filename: str) -> list[TypestrictError]:
        assert isinstance(node, ast.ClassDef)
        errors: list[TypestrictError] = []

        errors.extend(self._check_class_body(node, filename))

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                errors.extend(self._check_init_body(stmt, filename))

        return errors

    def _check_class_body(
        self,
        class_node: ast.ClassDef,
        filename: str,
    ) -> list[TypestrictError]:
        """Check class-level ``ast.Assign`` statements (not inside methods)."""
        errors: list[TypestrictError] = []

        for stmt in class_node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        errors.append(
                            TypestrictError(
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
    ) -> list[TypestrictError]:
        """Check ``self.attr = value`` patterns in ``__init__``.

        Uses ``_walk_no_nested_scopes`` so that assignments inside nested
        functions/classes are not falsely attributed to this ``__init__``.
        """
        errors: list[TypestrictError] = []
        self_name: str | None = _get_self_name(init_node)
        if self_name is None:
            return errors

        for stmt in _walk_no_nested_scopes(init_node):
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == self_name
                ):
                    errors.append(
                        TypestrictError(
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
