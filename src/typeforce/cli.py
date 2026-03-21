"""CLI entry-point for typeforce."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import click

from typeforce.checker import check_file
from typeforce.config import TypeforceConfig, load_config
from typeforce.errors import TypeforceError
from typeforce.formatters.json import JsonFormatter
from typeforce.formatters.text import TextFormatter

_PYTHON_GLOB = "**/*.py"


def _collect_python_files(path: Path, config: TypeforceConfig) -> list[Path]:
    """Recursively collect ``.py`` files under *path*, respecting exclusions."""
    if path.is_file():
        if path.suffix == ".py" and not config.is_file_excluded(str(path)):
            return [path]
        return []

    files: list[Path] = []
    for py_file in sorted(path.glob(_PYTHON_GLOB)):
        if not config.is_file_excluded(str(py_file)):
            files.append(py_file)
    return files


def _run_checks(
    paths: Sequence[Path],
    config: TypeforceConfig,
    selected_rules: list[str] | None,
) -> list[TypeforceError]:
    """Run typeforce checks over all *paths* and return the combined error list."""
    all_errors: list[TypeforceError] = []
    for path in paths:
        all_errors.extend(check_file(path, config, selected_rules))
    return sorted(all_errors, key=lambda e: (e.file, e.line, e.col))


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
    type=click.Choice(["text", "json"], case_sensitive=False),
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
    config = load_config(config_path)

    selected_rules: list[str] | None = None
    if select:
        selected_rules = [r.strip() for r in select.split(",") if r.strip()]

    python_files: list[Path] = []
    for path in paths:
        python_files.extend(_collect_python_files(path, config))

    errors = _run_checks(python_files, config, selected_rules)

    if output_format == "json":
        formatter: JsonFormatter | TextFormatter = JsonFormatter()
    else:
        formatter = TextFormatter()

    output = formatter.format(errors)
    click.echo(output)

    if fail_on_error and errors:
        sys.exit(1)


def main() -> None:
    """Package entry-point."""
    cli()


if __name__ == "__main__":
    main()
