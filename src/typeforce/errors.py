"""Error dataclass for typeforce violations."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TypeforceError:
    """Represents a single typeforce rule violation."""

    file: str
    line: int
    col: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.col}  {self.code}  {self.message}"
