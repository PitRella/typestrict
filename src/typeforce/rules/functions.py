"""TF002 / TF003 – function argument and return-type annotations."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError
from typeforce.rules.base import Rule

# Names of first arguments that are implicitly typed and should be skipped.
_IMPLICIT_SELF_NAMES: frozenset[str] = frozenset({"self", "cls"})


def _is_method(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Heuristic: a function is a method when its first arg is ``self`` or ``cls``."""
    args: list[ast.arg] = node.args.args
    return bool(args) and args[0].arg in _IMPLICIT_SELF_NAMES


class FunctionAnnotationRule(Rule):
    """TF002 / TF003 – function argument and return-type annotations."""

    code = "TF002"  # primary code; TF003 is also emitted
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef)

    def check(self, node: ast.AST, filename: str) -> list[TypeforceError]:
        assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        errors: list[TypeforceError] = []

        all_args = list(node.args.args)
        is_method = _is_method(node)
        start_index = 1 if is_method else 0

        # TF002 – argument annotations
        for arg in all_args[start_index:]:
            if arg.annotation is None:
                errors.append(
                    TypeforceError(
                        file=filename,
                        line=arg.lineno,
                        col=arg.col_offset,
                        code="TF002",
                        message=f"Argument '{arg.arg}' missing type annotation",
                    )
                )

        # Also check *args and **kwargs
        if node.args.vararg is not None and node.args.vararg.annotation is None:
            va = node.args.vararg
            errors.append(
                TypeforceError(
                    file=filename,
                    line=va.lineno,
                    col=va.col_offset,
                    code="TF002",
                    message=f"Argument '*{va.arg}' missing type annotation",
                )
            )

        if node.args.kwarg is not None and node.args.kwarg.annotation is None:
            kw = node.args.kwarg
            errors.append(
                TypeforceError(
                    file=filename,
                    line=kw.lineno,
                    col=kw.col_offset,
                    code="TF002",
                    message=f"Argument '**{kw.arg}' missing type annotation",
                )
            )

        # Keyword-only args
        for kwonly_arg in node.args.kwonlyargs:
            if kwonly_arg.annotation is None:
                errors.append(
                    TypeforceError(
                        file=filename,
                        line=kwonly_arg.lineno,
                        col=kwonly_arg.col_offset,
                        code="TF002",
                        message=f"Argument '{kwonly_arg.arg}' missing type annotation",
                    )
                )

        # TF003 – return annotation
        if node.returns is None:
            errors.append(
                TypeforceError(
                    file=filename,
                    line=node.lineno,
                    col=node.col_offset,
                    code="TF003",
                    message=f"Function '{node.name}' missing return type annotation",
                )
            )

        return errors
