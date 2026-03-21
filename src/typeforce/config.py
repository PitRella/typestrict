"""Configuration loading from pyproject.toml."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib  # type: ignore[no-redef]
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError:
            tomllib = None  # type: ignore[assignment]


_DEFAULT_EXCLUDE: list[str] = ["tests/", "migrations/", "conftest.py"]
_DEFAULT_IGNORE: list[str] = ["TF005"]


@dataclass
class TypeforceConfig:
    """Resolved typeforce configuration."""

    exclude: list[str] = field(default_factory=lambda: list(_DEFAULT_EXCLUDE))
    ignore: list[str] = field(default_factory=lambda: list(_DEFAULT_IGNORE))
    per_file_ignores: dict[str, list[str]] = field(default_factory=dict)
    strict: bool = False

    def is_rule_ignored(self, rule_code: str, file_path: str | None = None) -> bool:
        """Return True if this rule should be suppressed for the given file."""
        if rule_code in self.ignore:
            return True
        if file_path is not None:
            for pattern, codes in self.per_file_ignores.items():
                if _path_matches_pattern(file_path, pattern) and rule_code in codes:
                    return True
        return False

    def is_file_excluded(self, file_path: str) -> bool:
        """Return True if this file should be excluded from analysis."""
        for pattern in self.exclude:
            if _path_matches_pattern(file_path, pattern):
                return True
        return False


def _path_matches_pattern(file_path: str, pattern: str) -> bool:
    """Check if a file path matches an exclusion/per-file pattern."""
    path = Path(file_path)
    pattern_path = Path(pattern)

    # Match if the pattern is a suffix of the file path or appears in any part
    try:
        # Check if path is relative to the pattern (for directory patterns)
        if pattern.endswith("/"):
            dir_name = pattern.rstrip("/")
            return dir_name in path.parts
        # Check exact filename match or path suffix
        return (
            path.name == pattern
            or str(path).endswith(pattern)
            or str(path) == pattern
            or pattern in str(path)
        )
    except (ValueError, TypeError):
        return False


def load_config(search_path: Path | None = None) -> TypeforceConfig:
    """Load TypeforceConfig from the nearest pyproject.toml.

    Searches from *search_path* (defaults to cwd) upward until a pyproject.toml
    with a ``[tool.typeforce]`` section is found.  Returns default config if
    none is found or if the toml library is unavailable.
    """
    if tomllib is None:
        return TypeforceConfig()

    start = (search_path or Path.cwd()).resolve()
    for directory in [start, *start.parents]:
        candidate = directory / "pyproject.toml"
        if candidate.exists():
            try:
                with candidate.open("rb") as fh:
                    data = tomllib.load(fh)
                tf_section = data.get("tool", {}).get("typeforce", {})
                return _build_config(tf_section)
            except Exception:
                # Malformed toml or other I/O error – use defaults
                return TypeforceConfig()

    return TypeforceConfig()


def _build_config(section: dict[str, object]) -> TypeforceConfig:
    """Build a TypeforceConfig from a raw ``[tool.typeforce]`` mapping."""
    exclude: list[str] = list(section.get("exclude", _DEFAULT_EXCLUDE))  # type: ignore[arg-type]
    ignore: list[str] = list(section.get("ignore", _DEFAULT_IGNORE))  # type: ignore[arg-type]
    per_file_ignores: dict[str, list[str]] = dict(section.get("per_file_ignores", {}))  # type: ignore[arg-type]
    strict: bool = bool(section.get("strict", False))

    if strict and "TF005" in ignore:
        ignore.remove("TF005")

    return TypeforceConfig(
        exclude=exclude,
        ignore=ignore,
        per_file_ignores=per_file_ignores,
        strict=strict,
    )
