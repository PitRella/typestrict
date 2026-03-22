"""Tests for TF005 – loop and context-manager variable annotations."""
from __future__ import annotations

from must_annotate.checker import check_source
from must_annotate.config import MustAnnotateConfig
from must_annotate.errors import MustAnnotateError


def _check(source: str) -> list[MustAnnotateError]:
    config = MustAnnotateConfig(exclude=[], ignore=[], per_file_ignores={}, strict=True)
    return check_source(source, "<test>", config, selected_rules=["TF005"])


class TestTF005SyncLoops:

    def test_for_loop_flagged(self) -> None:
        errors = _check("for x in items:\n    pass\n")
        assert len(errors) == 1
        assert "x" in errors[0].message

    def test_underscore_skipped(self) -> None:
        errors = _check("for _ in items:\n    pass\n")
        assert errors == []

    def test_with_statement_flagged(self) -> None:
        errors = _check("with open('f') as fp:\n    pass\n")
        assert len(errors) == 1
        assert "fp" in errors[0].message

    def test_with_no_target_passes(self) -> None:
        errors = _check("with open('f'):\n    pass\n")
        assert errors == []


class TestTF005AsyncLoops:

    def test_async_for_flagged(self) -> None:
        source = "async def f() -> None:\n    async for x in items:\n        pass\n"
        errors = _check(source)
        assert len(errors) == 1
        assert "x" in errors[0].message

    def test_async_for_underscore_skipped(self) -> None:
        source = "async def f() -> None:\n    async for _ in items:\n        pass\n"
        errors = _check(source)
        assert errors == []

    def test_async_with_flagged(self) -> None:
        source = "async def f() -> None:\n    async with ctx() as val:\n        pass\n"
        errors = _check(source)
        assert len(errors) == 1
        assert "val" in errors[0].message

    def test_async_with_no_target_passes(self) -> None:
        source = "async def f() -> None:\n    async with ctx():\n        pass\n"
        errors = _check(source)
        assert errors == []

    def test_tf005_disabled_by_default(self) -> None:
        config = MustAnnotateConfig()  # default config: TF005 in ignore
        source = "async def f() -> None:\n    async for x in items:\n        pass\n"
        errors = check_source(source, "<test>", config)
        assert all(e.code != "TF005" for e in errors)
