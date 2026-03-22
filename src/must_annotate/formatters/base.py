"""Abstract base class for all must-annotate output formatters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from must_annotate.errors import MustAnnotateError


class BaseFormatter(ABC):
    """Base class for formatting must-annotate errors into a string output."""

    @abstractmethod
    def format(self, errors: list[MustAnnotateError]) -> str:
        """Format *errors* and return the result as a string."""
