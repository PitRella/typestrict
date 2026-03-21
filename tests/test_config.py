"""Tests for config loading and rule filtering."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from typeforce.config import TypeforceConfig, _build_config, _path_matches_pattern


class TestTypeforceConfig:
    """Unit tests for TypeforceConfig behaviour."""

    def test_default_ignore_tf005(self) -> None:
        config = TypeforceConfig()
        assert config.is_rule_ignored("TF005")

    def test_custom_ignore(self) -> None:
        config = TypeforceConfig(ignore=["TF001"])
        assert config.is_rule_ignored("TF001")
        assert not config.is_rule_ignored("TF002")

    def test_per_file_ignore(self) -> None:
        config = TypeforceConfig(
            ignore=[],
            per_file_ignores={"settings.py": ["TF001"]},
        )
        assert config.is_rule_ignored("TF001", file_path="settings.py")
        assert not config.is_rule_ignored("TF001", file_path="models.py")

    def test_is_file_excluded_by_dir(self) -> None:
        config = TypeforceConfig(exclude=["migrations/"])
        assert config.is_file_excluded("app/migrations/0001_initial.py")

    def test_is_file_excluded_by_name(self) -> None:
        config = TypeforceConfig(exclude=["conftest.py"])
        assert config.is_file_excluded("/project/tests/conftest.py")

    def test_is_file_not_excluded(self) -> None:
        config = TypeforceConfig(exclude=["migrations/"])
        assert not config.is_file_excluded("app/models.py")

    def test_strict_removes_tf005_from_ignore(self) -> None:
        section: dict[str, object] = {"strict": True, "ignore": ["TF005"]}
        config = _build_config(section)
        assert "TF005" not in config.ignore

    def test_strict_false_keeps_tf005_in_ignore(self) -> None:
        section: dict[str, object] = {"strict": False, "ignore": ["TF005"]}
        config = _build_config(section)
        assert "TF005" in config.ignore


class TestPathMatchesPattern:
    """Unit tests for _path_matches_pattern."""

    def test_directory_pattern(self) -> None:
        assert _path_matches_pattern("app/migrations/0001.py", "migrations/")

    def test_filename_pattern(self) -> None:
        assert _path_matches_pattern("/project/tests/conftest.py", "conftest.py")

    def test_no_match(self) -> None:
        assert not _path_matches_pattern("app/models.py", "migrations/")


class TestLoadConfig:
    """Integration tests for load_config using a temp pyproject.toml."""

    def test_load_from_pyproject(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            textwrap.dedent(
                """\
                [tool.typeforce]
                ignore = ["TF001"]
                strict = false
                """
            )
        )
        from typeforce.config import load_config

        config = load_config(tmp_path)
        assert "TF001" in config.ignore

    def test_defaults_when_no_pyproject(self, tmp_path: Path) -> None:
        from typeforce.config import load_config

        config = load_config(tmp_path)
        # Should return default config without crashing
        assert isinstance(config, TypeforceConfig)
