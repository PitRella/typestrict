"""Abstract base class for all typeforce output formatters."""
from __future__ import annotations

from abc import ABC, abstractmethod

from typeforce.errors import TypeforceError


class BaseFormatter(ABC):
    """Base class for formatting typeforce errors into a string output."""

    @abstractmethod
    def format(self, errors: list[TypeforceError]) -> str:
        """Format *errors* and return the result as a string."""
