"""Tests for TF001 – variable assignment without type annotation."""
from __future__ import annotations

import pytest

from typeforce.checker import check_source
from typeforce.config import TypeforceConfig
from typeforce.errors import TypeforceError
from tests.conftest import FIXTURES_DIR, run_checker


class TestTF001FailFixture:
    """Errors in variables_fail.py must match the expected annotations."""

    def test_expected_errors_found(self) -> None:
        errors, expected = run_checker("variables_fail.py", selected_rules=["TF001"])
        actual_pairs = [(e.line, e.code) for e in errors]
        for pair in expected:
            assert pair in actual_pairs, f"Expected {pair} not in {actual_pairs}"

    def test_error_count(self) -> None:
        errors, expected = run_checker("variables_fail.py", selected_rules=["TF001"])
        assert len(errors) == len(expected), (
            f"Expected {len(expected)} errors but got {len(errors)}: "
            + ", ".join(str(e) for e in errors)
        )

    def test_error_codes_are_tf001(self) -> None:
        errors, _ = run_checker("variables_fail.py", selected_rules=["TF001"])
        for error in errors:
            assert error.code == "TF001"


class TestTF001PassFixture:
    """variables_pass.py must not produce any TF001 errors."""

    def test_no_errors(self) -> None:
        errors, expected = run_checker("variables_pass.py", selected_rules=["TF001"])
        assert errors == [], f"Unexpected errors: {errors}"
        assert expected == [], "Pass fixture should not have expected errors annotated"


class TestTF001Specifics:
    """Unit-level checks for specific TF001 scenarios."""

    def _check(self, source: str) -> list[TypeforceError]:
        config = TypeforceConfig(exclude=[], ignore=[], per_file_ignores={}, strict=True)
        return check_source(source, "<test>", config, selected_rules=["TF001"])

    def test_plain_assignment_triggers(self) -> None:
        errors = self._check("x = 1\n")
        assert len(errors) == 1
        assert errors[0].code == "TF001"
        assert "x" in errors[0].message

    def test_annotated_assignment_passes(self) -> None:
        errors = self._check("x: int = 1\n")
        assert errors == []

    def test_dunder_skipped(self) -> None:
        errors = self._check('__version__ = "1.0"\n')
        assert errors == []

    def test_underscore_skipped(self) -> None:
        errors = self._check("_ = some_func()\n")
        assert errors == []

    def test_tuple_unpack_skipped(self) -> None:
        errors = self._check("a, b = func()\n")
        assert errors == []

    def test_aug_assign_skipped(self) -> None:
        errors = self._check("counter: int = 0\ncounter += 1\n")
        assert errors == []

    def test_inline_ignore_suppresses(self) -> None:
        errors = self._check("x = 1  # typeforce: ignore\n")
        assert errors == []

    def test_inline_ignore_specific_code_suppresses(self) -> None:
        errors = self._check("x = 1  # typeforce: ignore[TF001]\n")
        assert errors == []

    def test_inline_ignore_other_code_does_not_suppress(self) -> None:
        errors = self._check("x = 1  # typeforce: ignore[TF002]\n")
        assert len(errors) == 1

    def test_multiple_assignments(self) -> None:
        source = "a = 1\nb: int = 2\nc = 3\n"
        errors = self._check(source)
        assert len(errors) == 2
        names = [e.message for e in errors]
        assert any("'a'" in m for m in names)
        assert any("'c'" in m for m in names)

    def test_error_has_correct_location(self) -> None:
        errors = self._check("x = 1\n")
        assert errors[0].line == 1
        assert errors[0].col == 0

    def test_config_ignore_suppresses(self) -> None:
        config = TypeforceConfig(
            exclude=[], ignore=["TF001"], per_file_ignores={}, strict=False
        )
        errors = check_source("x = 1\n", "<test>", config)
        assert errors == []
