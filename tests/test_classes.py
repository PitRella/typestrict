"""Tests for TF004 – class attribute annotations."""
from __future__ import annotations

import pytest

from typestrict.checker import check_source
from typestrict.config import TypestrictConfig
from typestrict.errors import TypestrictError
from tests.conftest import run_checker


def _check(source: str, rules: list[str] | None = None) -> list[TypestrictError]:
    config = TypestrictConfig(exclude=[], ignore=[], per_file_ignores={}, strict=True)
    return check_source(source, "<test>", config, selected_rules=rules)


class TestTF004FailFixture:
    """Errors in classes_fail.py must match the expected annotations."""

    def test_expected_errors_found(self) -> None:
        errors, expected = run_checker("classes_fail.py", selected_rules=["TF004"])
        actual_pairs = [(e.line, e.code) for e in errors]
        for pair in expected:
            assert pair in actual_pairs, f"Expected {pair} not found in {actual_pairs}"

    def test_error_count(self) -> None:
        errors, expected = run_checker("classes_fail.py", selected_rules=["TF004"])
        assert len(errors) == len(expected), (
            f"Expected {len(expected)} but got {len(errors)}: "
            + ", ".join(str(e) for e in errors)
        )


class TestTF004PassFixture:
    """classes_pass.py must not produce any TF004 errors."""

    def test_no_errors(self) -> None:
        errors, _ = run_checker("classes_pass.py", selected_rules=["TF004"])
        assert errors == [], f"Unexpected errors: {errors}"


class TestTF004Specifics:
    """Unit-level checks for specific TF004 scenarios."""

    def test_self_assign_in_init_triggers(self) -> None:
        source = (
            "class C:\n"
            "    def __init__(self) -> None:\n"
            "        self.x = 1\n"
        )
        errors = _check(source, ["TF004"])
        assert len(errors) == 1
        assert errors[0].code == "TF004"
        assert "self.x" in errors[0].message

    def test_annotated_self_assign_passes(self) -> None:
        source = (
            "class C:\n"
            "    def __init__(self) -> None:\n"
            "        self.x: int = 1\n"
        )
        errors = _check(source, ["TF004"])
        assert errors == []

    def test_class_level_assign_triggers(self) -> None:
        source = "class C:\n    count = 0\n"
        errors = _check(source, ["TF004"])
        assert len(errors) == 1
        assert errors[0].code == "TF004"
        assert "count" in errors[0].message

    def test_class_level_annotated_passes(self) -> None:
        source = "class C:\n    count: int = 0\n"
        errors = _check(source, ["TF004"])
        assert errors == []

    def test_multiple_self_assigns_trigger_each(self) -> None:
        source = (
            "class C:\n"
            "    def __init__(self) -> None:\n"
            "        self.a = 1\n"
            "        self.b = 2\n"
        )
        errors = _check(source, ["TF004"])
        assert len(errors) == 2

    def test_non_init_self_assign_not_checked(self) -> None:
        """Only __init__ is currently inspected for self.x patterns."""
        source = (
            "class C:\n"
            "    def setup(self) -> None:\n"
            "        self.x = 1\n"
        )
        errors = _check(source, ["TF004"])
        # setup() is not __init__ – TF004 rule only triggers for __init__
        assert errors == []

    def test_config_ignore_tf004(self) -> None:
        config = TypestrictConfig(
            exclude=[], ignore=["TF004"], per_file_ignores={}, strict=False
        )
        source = "class C:\n    x = 1\n"
        errors = check_source(source, "<test>", config)
        assert errors == []

    def test_nested_function_in_init_not_flagged(self) -> None:
        # self.attr inside a nested function should NOT be attributed to __init__
        source = (
            "class C:\n"
            "    def __init__(self) -> None:\n"
            "        def helper() -> None:\n"
            "            self.x = 1\n"  # nested scope — should not be flagged
            "        helper()\n"
        )
        errors = _check(source, ["TF004"])
        assert errors == []

    def test_self_assign_inside_if_flagged(self) -> None:
        # Assignment inside an if-block in __init__ SHOULD still be flagged
        source = (
            "class C:\n"
            "    def __init__(self, flag: bool) -> None:\n"
            "        if flag:\n"
            "            self.x = 1\n"
        )
        errors = _check(source, ["TF004"])
        assert len(errors) == 1
        assert "self.x" in errors[0].message
