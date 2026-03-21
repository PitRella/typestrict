"""typeforce – enforce type annotation presence in Python code."""
from typeforce.checker import TypeforceChecker, check_file, check_source
from typeforce.cli import Runner
from typeforce.config import TypeforceConfig
from typeforce.errors import TypeforceError
from typeforce.formatters.base import BaseFormatter
from typeforce.formatters.json import JsonFormatter
from typeforce.formatters.text import TextFormatter
from typeforce.rules import RULES, Rule

__version__: str = "0.1.0"

__all__ = [
    "__version__",
    # Core types
    "TypeforceError",
    "TypeforceConfig",
    "TypeforceChecker",
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
