"""Abstract base class for all typestrict output formatters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from typestrict.errors import TypestrictError


class BaseFormatter(ABC):
    """Base class for formatting typestrict errors into a string output."""

    @abstractmethod
    def format(self, errors: list[TypestrictError]) -> str:
        """Format *errors* and return the result as a string."""
