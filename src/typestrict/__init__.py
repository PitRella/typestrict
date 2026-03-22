"""typestrict – enforce type annotation presence in Python code."""
from typestrict.checker import TypestrictChecker, check_file, check_source
from typestrict.cli import Runner
from typestrict.config import TypestrictConfig
from typestrict.errors import TypestrictError
from typestrict.formatters.base import BaseFormatter
from typestrict.formatters.json import JsonFormatter
from typestrict.formatters.text import TextFormatter
from typestrict.rules import RULES, Rule

__version__: str = "0.1.0"

__all__ = [
    "__version__",
    # Core types
    "TypestrictError",
    "TypestrictConfig",
    "TypestrictChecker",
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
