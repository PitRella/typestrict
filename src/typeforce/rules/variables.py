"""TF001 – variable assignment without a type annotation."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError

_RULE_CODE: str = "TF001"
_DUNDER_PREFIX: str = "__"


def _is_dunder_name(name: str) -> bool:
    """Return True for names like ``__all__``, ``__version__``, etc."""
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


def check_assignment(
    node: ast.Assign,
    filename: str,
) -> list[TypeforceError]:
    """Check an ``ast.Assign`` node for TF001 violations.

    Rules:
    - Skip dunder names (``__all__``, ``__version__``, …)
    - Skip ``_ = …`` (unused value convention)
    - Flag all names in tuple-unpacking targets (``a, b = func()``)
    - ``ast.AugAssign`` nodes (``x += 1``) are never passed here; the caller
      is responsible for filtering those out.
    """
    errors: list[TypeforceError] = []

    for target in node.targets:
        for name in _collect_names(target):
            if name == "_":
                continue
            if _is_dunder_name(name):
                continue

            errors.append(
                TypeforceError(
                    file=filename,
                    line=node.lineno,
                    col=node.col_offset,
                    code=_RULE_CODE,
                    message=f"Variable '{name}' missing type annotation",
                )
            )

    return errors
