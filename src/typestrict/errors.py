"""Error dataclass for typestrict violations."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TypestrictError:
    """Represents a single typestrict rule violation."""

    file: str
    line: int
    col: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.col}  {self.code}  {self.message}"
