"""Tests for the CLI interface."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from typeforce.cli import cli
from tests.conftest import FIXTURES_DIR


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def empty_config_dir(tmp_path: Path) -> Path:
    """A directory with an empty [tool.typeforce] section (no excludes/ignores)."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.typeforce]\nexclude = []\nignore = []\nstrict = true\n"
    )
    return tmp_path


class TestCheckCommand:
    """Integration tests for ``typeforce check``."""

    def test_check_single_file_text_output(
        self, runner: CliRunner, empty_config_dir: Path
    ) -> None:
        fixture = str(FIXTURES_DIR / "variables_fail.py")
        result = runner.invoke(
            cli, ["check", "--config", str(empty_config_dir), fixture]
        )
        assert result.exit_code == 0
        assert "TF001" in result.output

    def test_check_directory(self, runner: CliRunner, tmp_path: Path) -> None:
        sample = tmp_path / "sample.py"
        sample.write_text("x = 1\n")
        # tmp_path contains its own pyproject.toml from empty_config_dir fixture
        # just let load_config search from cwd – no excludes apply to tmp_path
        result = runner.invoke(cli, ["check", str(tmp_path)])
        assert "TF001" in result.output

    def test_fail_on_error_exit_code(
        self, runner: CliRunner, empty_config_dir: Path
    ) -> None:
        fixture = str(FIXTURES_DIR / "variables_fail.py")
        result = runner.invoke(
            cli,
            ["check", "--config", str(empty_config_dir), "--fail-on-error", fixture],
        )
        assert result.exit_code == 1

    def test_no_errors_exit_code_zero(self, runner: CliRunner, tmp_path: Path) -> None:
        clean = tmp_path / "clean.py"
        clean.write_text("x: int = 1\n")
        result = runner.invoke(cli, ["check", "--fail-on-error", str(clean)])
        assert result.exit_code == 0

    def test_json_format(
        self, runner: CliRunner, empty_config_dir: Path
    ) -> None:
        fixture = str(FIXTURES_DIR / "variables_fail.py")
        result = runner.invoke(
            cli,
            ["check", "--config", str(empty_config_dir), "--format", "json", fixture],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert all("code" in item for item in data)
        assert any(item["code"] == "TF001" for item in data)

    def test_select_filters_rules(self, runner: CliRunner, tmp_path: Path) -> None:
        source = tmp_path / "mixed.py"
        # This will produce TF001 and TF003; we select only TF001
        source.write_text("x = 1\ndef f(): pass\n")
        result = runner.invoke(
            cli, ["check", "--select", "TF001", str(source)]
        )
        assert "TF001" in result.output
        assert "TF003" not in result.output

    def test_clean_file_text_output(self, runner: CliRunner, tmp_path: Path) -> None:
        clean = tmp_path / "clean.py"
        clean.write_text("x: int = 1\n")
        result = runner.invoke(cli, ["check", str(clean)])
        assert result.exit_code == 0
        assert "No errors found" in result.output

    def test_json_no_errors(self, runner: CliRunner, tmp_path: Path) -> None:
        clean = tmp_path / "clean.py"
        clean.write_text("x: int = 1\n")
        result = runner.invoke(cli, ["check", "--format", "json", str(clean)])
        data = json.loads(result.output)
        assert data == []

    def test_multiple_paths(self, runner: CliRunner, tmp_path: Path) -> None:
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x = 1\n")
        f2.write_text("y = 2\n")
        result = runner.invoke(cli, ["check", str(f1), str(f2)])
        assert "TF001" in result.output
        # Both files should be mentioned
        assert "a.py" in result.output
        assert "b.py" in result.output

    def test_summary_line_in_text(self, runner: CliRunner, tmp_path: Path) -> None:
        f = tmp_path / "x.py"
        f.write_text("a = 1\nb = 2\n")
        result = runner.invoke(cli, ["check", str(f)])
        assert "Found" in result.output
        assert "error" in result.output
