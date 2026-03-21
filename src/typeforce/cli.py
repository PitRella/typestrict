"""CLI entry-point for typeforce."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import ClassVar, Sequence

import click

from typeforce.checker import check_file
from typeforce.config import TypeforceConfig
from typeforce.errors import TypeforceError
from typeforce.formatters.base import BaseFormatter
from typeforce.formatters.json import JsonFormatter
from typeforce.formatters.text import TextFormatter


class Runner:
    """Collects Python files and runs typeforce checks across them."""

    _PYTHON_GLOB: ClassVar[str] = "**/*.py"
    _FORMATTERS: ClassVar[dict[str, type[BaseFormatter]]] = {
        "text": TextFormatter,
        "json": JsonFormatter,
    }

    _config: TypeforceConfig
    _selected_rules: list[str] | None

    def __init__(
        self,
        config: TypeforceConfig,
        selected_rules: list[str] | None = None,
    ) -> None:
        self._config: TypeforceConfig = config
        self._selected_rules: list[str] | None = selected_rules

    def collect_files(self, paths: Sequence[Path]) -> list[Path]:
        """Recursively collect ``.py`` files under *paths*, respecting exclusions."""
        files: list[Path] = []
        for path in paths:
            files.extend(self._collect_from(path))
        return files

    def run(self, paths: Sequence[Path]) -> list[TypeforceError]:
        """Run checks on all collected files and return sorted errors."""
        all_errors: list[TypeforceError] = []
        for path in self.collect_files(paths):
            all_errors.extend(check_file(path, self._config, self._selected_rules))
        return sorted(all_errors, key=lambda e: (e.file, e.line, e.col))

    def formatter(self, output_format: str) -> BaseFormatter:
        """Return the formatter instance for the given *output_format* key."""
        formatter_cls = self._FORMATTERS.get(output_format, TextFormatter)
        return formatter_cls()

    def _collect_from(self, path: Path) -> list[Path]:
        if path.is_file():
            if path.suffix == ".py" and not self._config.is_file_excluded(str(path)):
                return [path]
            return []

        return [
            f for f in sorted(path.glob(self._PYTHON_GLOB))
            if not self._config.is_file_excluded(str(f))
        ]


@click.group()
def cli() -> None:
    """typeforce – enforce type annotation presence in Python code."""


@cli.command("check")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(list(Runner._FORMATTERS), case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--select",
    "select",
    default=None,
    help="Comma-separated list of rule codes to enable (e.g. TF001,TF002).",
)
@click.option(
    "--fail-on-error",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any errors are found.",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to a directory containing pyproject.toml (defaults to cwd).",
)
def check_command(
    paths: tuple[Path, ...],
    output_format: str,
    select: str | None,
    fail_on_error: bool,
    config_path: Path | None,
) -> None:
    """Check one or more files/directories for missing type annotations."""
    config: TypeforceConfig = TypeforceConfig.from_pyproject(config_path)
    selected_rules: list[str] | None = (
        [r.strip() for r in select.split(",") if r.strip()] if select else None
    )
    runner: Runner = Runner(config, selected_rules)
    errors: list[TypeforceError] = runner.run(paths)

    click.echo(runner.formatter(output_format).format(errors))

    if fail_on_error and errors:
        sys.exit(1)


def main() -> None:
    """Package entry-point."""
    cli()


if __name__ == "__main__":
    main()
