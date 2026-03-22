"""Error dataclass for must-annotate violations."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MustAnnotateError:
    """Represents a single must-annotate rule violation."""

    file: str
    line: int
    col: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.col}  {self.code}  {self.message}"
