"""JSON formatter for CI/CD integration."""
from __future__ import annotations

import json
from typing import TypedDict

from typestrict.errors import TypestrictError
from typestrict.formatters.base import BaseFormatter


class _ErrorDict(TypedDict):
    """JSON shape of a single typestrict error."""

    file: str
    line: int
    col: int
    code: str
    message: str


class JsonFormatter(BaseFormatter):
    """Format errors as a JSON array."""

    def format(self, errors: list[TypestrictError]) -> str:
        """Return a JSON string representing the list of errors."""
        payload: list[_ErrorDict] = [
            {
                "file": e.file,
                "line": e.line,
                "col": e.col,
                "code": e.code,
                "message": e.message,
            }
            for e in errors
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False)
