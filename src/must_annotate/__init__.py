"""must-annotate – enforce type annotation presence in Python code."""
from must_annotate.checker import MustAnnotateChecker, check_file, check_source
from must_annotate.cli import Runner
from must_annotate.config import MustAnnotateConfig
from must_annotate.errors import MustAnnotateError
from must_annotate.formatters.base import BaseFormatter
from must_annotate.formatters.json import JsonFormatter
from must_annotate.formatters.text import TextFormatter
from must_annotate.rules import RULES, Rule

__version__: str = "0.1.0"

__all__ = [
    "__version__",
    # Core types
    "MustAnnotateError",
    "MustAnnotateConfig",
    "MustAnnotateChecker",
    # Rules
    "Rule",
    "RULES",
    # Formatters
    "BaseFormatter",
    "TextFormatter",
    "JsonFormatter",
    # Runner
    "Runner",
    # Convenience API
    "check_source",
    "check_file",
]
