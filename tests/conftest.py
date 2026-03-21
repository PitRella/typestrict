"""Shared pytest fixtures and helpers."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from typestrict.checker import check_source
from typestrict.config import TypestrictConfig
from typestrict.errors import TypestrictError

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Matches a trailing annotation comment that consists *only* of rule codes,
# e.g. ``# TF001``, ``# TF002 TF003``, ``# TF002 TF002 TF003``.
# The comment must be the last thing on the line and must not contain any other
# prose words – this distinguishes annotation markers from description comments.
_ANNOTATION_COMMENT_RE = re.compile(r"#\s*((?:TF\d{3}\s*)+)$")
_CODE_RE = re.compile(r"TF\d{3}")


def parse_expected_errors(source: str, filename: str) -> list[tuple[int, str]]:
    """Return ``[(line_number, code), …]`` from inline fixture comments.

    A line such as::

        a = 3  # TF001

    will yield ``(lineno, 'TF001')``.  Multiple codes on one line are supported::

        def f(x, y):  # TF002 TF002 TF003

    Comments that contain other prose (e.g. ``# ok – dunder``) are ignored.
    """
    expected: list[tuple[int, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        # Strip inline suppression comments – they are not expected-error markers
        stripped = line.rstrip()
        match = _ANNOTATION_COMMENT_RE.search(stripped)
        if match is None:
            continue
        for code in _CODE_RE.findall(match.group(1)):
            expected.append((lineno, code))
    return expected


def run_checker(
    fixture_name: str,
    extra_config: TypestrictConfig | None = None,
    selected_rules: list[str] | None = None,
) -> tuple[list[TypestrictError], list[tuple[int, str]]]:
    """Run the checker on a fixture file and return (actual_errors, expected_errors)."""
    fixture_path = FIXTURES_DIR / fixture_name
    source = fixture_path.read_text(encoding="utf-8")

    config = extra_config or TypestrictConfig(
        exclude=[],
        ignore=[],  # Enable ALL rules for testing
        per_file_ignores={},
        strict=True,
    )

    errors = check_source(source, str(fixture_path), config, selected_rules)
    expected = parse_expected_errors(source, str(fixture_path))
    return errors, expected


@pytest.fixture()
def default_config() -> TypestrictConfig:
    """Return a default TypestrictConfig suitable for tests (all rules enabled)."""
    return TypestrictConfig(
        exclude=[],
        ignore=[],
        per_file_ignores={},
        strict=True,
    )
