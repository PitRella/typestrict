"""Configuration loading from pyproject.toml."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, TypedDict

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib: Any = None  # type: ignore[no-redef]


class _TomlSection(TypedDict, total=False):
    """Shape of the raw ``[tool.must-annotate]`` TOML table."""

    exclude: list[str]
    ignore: list[str]
    per_file_ignores: dict[str, list[str]]
    strict: bool


@dataclass
class MustAnnotateConfig:
    """Resolved must-annotate configuration."""

    DEFAULT_EXCLUDE: ClassVar[tuple[str, ...]] = ("tests/", "migrations/", "conftest.py")
    DEFAULT_IGNORE: ClassVar[tuple[str, ...]] = ("TF005",)

    exclude: list[str] = field(default_factory=lambda: list(MustAnnotateConfig.DEFAULT_EXCLUDE))
    ignore: list[str] = field(default_factory=lambda: list(MustAnnotateConfig.DEFAULT_IGNORE))
    per_file_ignores: dict[str, list[str]] = field(default_factory=dict)
    strict: bool = False

    @classmethod
    def from_dict(cls, section: _TomlSection) -> MustAnnotateConfig:
        """Build a ``MustAnnotateConfig`` from a raw ``[tool.must-annotate]`` mapping."""
        exclude: list[str] = list(section.get("exclude", cls.DEFAULT_EXCLUDE))
        ignore: list[str] = list(section.get("ignore", cls.DEFAULT_IGNORE))
        per_file_ignores: dict[str, list[str]] = dict(section.get("per_file_ignores", {}))
        strict: bool = bool(section.get("strict", False))

        if strict and "TF005" in ignore:
            ignore.remove("TF005")

        return cls(
            exclude=exclude,
            ignore=ignore,
            per_file_ignores=per_file_ignores,
            strict=strict,
        )

    @classmethod
    def from_pyproject(cls, search_path: Path | None = None) -> MustAnnotateConfig:
        """Load config from the nearest ``pyproject.toml``.

        Searches from *search_path* (defaults to cwd) upward until a
        ``pyproject.toml`` with a ``[tool.must-annotate]`` section is found.
        Returns a default config if none is found or tomllib is unavailable.
        """
        if tomllib is None:
            return cls()

        start = (search_path or Path.cwd()).resolve()
        for directory in [start, *start.parents]:
            candidate = directory / "pyproject.toml"
            if candidate.exists():
                try:
                    with candidate.open("rb") as fh:
                        data = tomllib.load(fh)
                    section: _TomlSection = data.get("tool", {}).get("must-annotate", {})
                    return cls.from_dict(section)
                except Exception:
                    return cls()

        return cls()

    def is_rule_ignored(self, rule_code: str, file_path: str | None = None) -> bool:
        """Return True if this rule should be suppressed for the given file."""
        if rule_code in self.ignore:
            return True
        if file_path is not None:
            for pattern, codes in self.per_file_ignores.items():
                if self._matches_pattern(file_path, pattern) and rule_code in codes:
                    return True
        return False

    def is_file_excluded(self, file_path: str) -> bool:
        """Return True if this file should be excluded from analysis."""
        return any(self._matches_pattern(file_path, p) for p in self.exclude)

    @staticmethod
    def _matches_pattern(file_path: str, pattern: str) -> bool:
        """Return True if *file_path* matches the given exclusion *pattern*."""
        path = Path(file_path)
        try:
            if pattern.endswith("/"):
                return pattern.rstrip("/") in path.parts
            return (
                path.name == pattern
                or str(path).endswith(pattern)
                or str(path) == pattern
                or pattern in str(path)
            )
        except (ValueError, TypeError):
            return False


def load_config(search_path: Path | None = None) -> MustAnnotateConfig:
    """Convenience wrapper around ``MustAnnotateConfig.from_pyproject``."""
    return MustAnnotateConfig.from_pyproject(search_path)
