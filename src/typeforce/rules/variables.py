"""TF001 – variable assignment without a type annotation."""
from __future__ import annotations

import ast

from typeforce.errors import TypeforceError

_RULE_CODE: str = "TF001"
_DUNDER_PREFIX: str = "__"


def _is_dunder_name(name: str) -> bool:
    """Return True for names like ``__all__``, ``__version__``, etc."""
    return name.startswith(_DUNDER_PREFIX) and name.endswith(_DUNDER_PREFIX)


def _is_simple_name_target(target: ast.expr) -> tuple[bool, str]:
    """Return (is_simple_name, variable_name) for an assignment target.

    Returns (False, "") for tuple-unpacking or other complex targets.
    """
    if isinstance(target, ast.Name):
        return True, target.id
    return False, ""


def check_assignment(
    node: ast.Assign,
    filename: str,
) -> list[TypeforceError]:
    """Check an ``ast.Assign`` node for TF001 violations.

    Rules:
    - Skip dunder names (``__all__``, ``__version__``, …)
    - Skip ``_ = …`` (unused value convention)
    - Skip tuple-unpacking targets (``a, b = func()``)
    - ``ast.AugAssign`` nodes (``x += 1``) are never passed here; the caller
      is responsible for filtering those out.
    """
    errors: list[TypeforceError] = []

    for target in node.targets:
        is_simple, name = _is_simple_name_target(target)
        if not is_simple:
            # Tuple unpacking – skip
            continue
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
