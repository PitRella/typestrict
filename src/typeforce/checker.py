"""Main AST visitor that orchestrates all typeforce rules."""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Sequence

from typeforce.config import TypeforceConfig
from typeforce.errors import TypeforceError
from typeforce.rules import RULES
from typeforce.rules.base import Rule

# Matches:  # typeforce: ignore  or  # typeforce: ignore[TF001,TF002]
_INLINE_IGNORE_RE = re.compile(
    r"#\s*typeforce:\s*ignore(?:\[([A-Z0-9,\s]+)\])?"
)


def _parse_inline_ignores(source_lines: list[str]) -> dict[int, set[str]]:
    """Return a mapping of {1-based line number -> set of ignored codes}.

    An empty set means *all* codes are suppressed on that line
    (bare ``# typeforce: ignore``).
    """
    suppressed: dict[int, set[str]] = {}
    for lineno, line in enumerate(source_lines, start=1):
        match = _INLINE_IGNORE_RE.search(line)
        if match is None:
            continue
        codes_str = match.group(1)
        codes = {c.strip() for c in codes_str.split(",") if c.strip()} if codes_str else set()
        suppressed[lineno] = codes
    return suppressed


class _ScopeStack:
    """Lightweight stack that tracks whether we are inside a class."""

    def __init__(self) -> None:
        self._class_depth: int = 0

    def enter_class(self) -> None:
        self._class_depth += 1

    def leave_class(self) -> None:
        self._class_depth -= 1

    @property
    def inside_class(self) -> bool:
        return self._class_depth > 0


class TypeforceChecker(ast.NodeVisitor):
    """Walk an AST and collect all typeforce rule violations.

    Rules are discovered automatically from the ``RULES`` registry.
    The checker builds a dispatch table keyed by AST node type so that
    each ``visit()`` call only invokes rules that declared interest in
    that node type.
    """

    def __init__(
        self,
        source: str,
        filename: str,
        config: TypeforceConfig,
        selected_rules: Sequence[str] | None = None,
        rules: list[Rule] | None = None,
    ) -> None:
        self._filename = filename
        self._config = config
        self._selected_rules: frozenset[str] | None = (
            frozenset(selected_rules) if selected_rules is not None else None
        )
        self._errors: list[TypeforceError] = []
        self._inline_ignores: dict[int, set[str]] = _parse_inline_ignores(
            source.splitlines()
        )
        self._scope = _ScopeStack()
        self._dispatch = self._build_dispatch(rules if rules is not None else RULES)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @classmethod
    def from_file(
        cls,
        path: Path,
        config: TypeforceConfig,
        selected_rules: Sequence[str] | None = None,
    ) -> "TypeforceChecker":
        """Construct a checker by reading *path* from disk."""
        source = path.read_text(encoding="utf-8")
        return cls(source, str(path), config, selected_rules)

    def run(self, tree: ast.AST) -> list[TypeforceError]:
        """Walk *tree* and return all collected errors."""
        self._errors.clear()
        self.visit(tree)
        return list(self._errors)

    # ------------------------------------------------------------------
    # Visitor
    # ------------------------------------------------------------------

    def visit(self, node: ast.AST) -> None:
        """Dispatch *node* to matching rules, then recurse into children.

        ``ast.ClassDef`` is handled specially so that ``_ScopeStack``
        stays accurate while its body is visited.
        """
        if isinstance(node, ast.ClassDef):
            self._apply_rules(node)
            self._scope.enter_class()
            self.generic_visit(node)
            self._scope.leave_class()
        else:
            self._apply_rules(node)
            self.generic_visit(node)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_dispatch(rules: list[Rule]) -> dict[type[ast.AST], list[Rule]]:
        """Build a ``{NodeType: [rules]}`` table from the rule list."""
        dispatch: dict[type[ast.AST], list[Rule]] = {}
        for rule in rules:
            for node_type in rule.node_types:
                dispatch.setdefault(node_type, []).append(rule)
        return dispatch

    def _apply_rules(self, node: ast.AST) -> None:
        """Run every rule registered for this node type."""
        for rule in self._dispatch.get(type(node), []):
            if rule.skip_in_class_body and self._scope.inside_class:
                continue
            for error in rule.check(node, self._filename):
                self._record(error)

    def _record(self, error: TypeforceError) -> None:
        """Apply all filters and append the error if it should be reported."""
        if not self._is_rule_active(error.code):
            return
        if self._is_inline_suppressed(error.line, error.code):
            return
        self._errors.append(error)

    def _is_rule_active(self, code: str) -> bool:
        if self._selected_rules is not None and code not in self._selected_rules:
            return False
        if self._config.is_rule_ignored(code, self._filename):
            return False
        return True

    def _is_inline_suppressed(self, lineno: int, code: str) -> bool:
        ignored = self._inline_ignores.get(lineno)
        if ignored is None:
            return False
        return len(ignored) == 0 or code in ignored


def check_source(
    source: str,
    filename: str,
    config: TypeforceConfig,
    selected_rules: Sequence[str] | None = None,
) -> list[TypeforceError]:
    """Parse *source* and return all typeforce errors.

    This is the primary programmatic API.
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return [
            TypeforceError(
                file=filename,
                line=exc.lineno or 1,
                col=exc.offset or 0,
                code="TF000",
                message=f"SyntaxError: {exc.msg}",
            )
        ]

    checker = TypeforceChecker(source, filename, config, selected_rules)
    return checker.run(tree)


def check_file(
    path: Path,
    config: TypeforceConfig,
    selected_rules: Sequence[str] | None = None,
) -> list[TypeforceError]:
    """Read *path* from disk and return all typeforce errors."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            TypeforceError(
                file=str(path),
                line=0,
                col=0,
                code="TF000",
                message=f"Cannot read file: {exc}",
            )
        ]
    return check_source(source, str(path), config, selected_rules)
