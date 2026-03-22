"""Tests for TF002 / TF003 – function argument and return-type annotations."""
from __future__ import annotations

import pytest

from must_annotate.checker import check_source
from must_annotate.config import MustAnnotateConfig
from must_annotate.errors import MustAnnotateError
from tests.conftest import run_checker


def _check(source: str, rules: list[str] | None = None) -> list[MustAnnotateError]:
    config = MustAnnotateConfig(exclude=[], ignore=[], per_file_ignores={}, strict=True)
    return check_source(source, "<test>", config, selected_rules=rules)


class TestTF002and003FailFixture:
    """Errors in functions_fail.py must match the expected annotations."""

    def test_expected_errors_found(self) -> None:
        errors, expected = run_checker(
            "functions_fail.py", selected_rules=["TF002", "TF003"]
        )
        actual_pairs = [(e.line, e.code) for e in errors]
        for pair in expected:
            assert pair in actual_pairs, f"Expected {pair} not found in {actual_pairs}"

    def test_error_count(self) -> None:
        errors, expected = run_checker(
            "functions_fail.py", selected_rules=["TF002", "TF003"]
        )
        assert len(errors) == len(expected), (
            f"Expected {len(expected)} but got {len(errors)}: "
            + ", ".join(str(e) for e in errors)
        )


class TestTF002and003PassFixture:
    """functions_pass.py must not produce any TF002/TF003 errors."""

    def test_no_errors(self) -> None:
        errors, _ = run_checker(
            "functions_pass.py", selected_rules=["TF002", "TF003"]
        )
        assert errors == [], f"Unexpected errors: {errors}"


class TestTF002Arguments:
    """Unit tests for TF002."""

    def test_unannotated_arg_triggers(self) -> None:
        errors = _check("def f(x) -> None: pass\n", ["TF002"])
        assert len(errors) == 1
        assert errors[0].code == "TF002"
        assert "'x'" in errors[0].message

    def test_annotated_arg_passes(self) -> None:
        errors = _check("def f(x: int) -> None: pass\n", ["TF002"])
        assert errors == []

    def test_self_skipped(self) -> None:
        errors = _check(
            "class C:\n    def m(self, x: int) -> None: pass\n", ["TF002"]
        )
        assert errors == []

    def test_cls_skipped(self) -> None:
        errors = _check(
            "class C:\n    @classmethod\n    def m(cls, x: int) -> None: pass\n",
            ["TF002"],
        )
        assert errors == []

    def test_multiple_unannotated_args(self) -> None:
        errors = _check("def f(x, y) -> None: pass\n", ["TF002"])
        assert len(errors) == 2

    def test_vararg_unannotated_triggers(self) -> None:
        errors = _check("def f(*args) -> None: pass\n", ["TF002"])
        assert any("*args" in e.message for e in errors)

    def test_kwarg_unannotated_triggers(self) -> None:
        errors = _check("def f(**kwargs) -> None: pass\n", ["TF002"])
        assert any("**kwargs" in e.message for e in errors)

    def test_kwonly_unannotated_triggers(self) -> None:
        errors = _check("def f(*, key) -> None: pass\n", ["TF002"])
        assert any("'key'" in e.message for e in errors)


class TestTF003ReturnType:
    """Unit tests for TF003."""

    def test_missing_return_annotation_triggers(self) -> None:
        errors = _check("def f() -> None: pass\n"[::-1][::-1], ["TF003"])
        assert errors == []  # has annotation, check inverse below

    def test_missing_return_annotation(self) -> None:
        errors = _check("def f(): pass\n", ["TF003"])
        assert len(errors) == 1
        assert errors[0].code == "TF003"
        assert "'f'" in errors[0].message

    def test_annotated_return_passes(self) -> None:
        errors = _check("def f() -> int: return 1\n", ["TF003"])
        assert errors == []

    def test_none_return_passes(self) -> None:
        errors = _check("def f() -> None: pass\n", ["TF003"])
        assert errors == []

    def test_async_missing_return_triggers(self) -> None:
        errors = _check("async def f(): pass\n", ["TF003"])
        assert len(errors) == 1
        assert errors[0].code == "TF003"

    def test_async_annotated_return_passes(self) -> None:
        errors = _check("async def f() -> None: pass\n", ["TF003"])
        assert errors == []

    def test_inline_ignore_suppresses_tf003(self) -> None:
        source = "def f(): pass  # must-annotate: ignore[TF003]\n"
        errors = _check(source, ["TF003"])
        assert errors == []


class TestPositionalOnlyArgs:
    """Edge cases for positional-only parameters (PEP 570)."""

    def test_posonly_unannotated_flagged(self) -> None:
        errors = _check("def f(x, /, y: int) -> None: pass\n", ["TF002"])
        assert len(errors) == 1
        assert "x" in errors[0].message

    def test_posonly_annotated_passes(self) -> None:
        errors = _check("def f(x: int, /, y: int) -> None: pass\n", ["TF002"])
        assert errors == []

    def test_posonly_self_skipped_in_method(self) -> None:
        # self as positional-only is unusual but valid: def method(self, /, x)
        source = (
            "class C:\n"
            "    def method(self, /, x: int) -> None: pass\n"
        )
        errors = _check(source, ["TF002"])
        assert errors == []
