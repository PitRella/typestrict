"""JSON formatter for CI/CD integration."""
from __future__ import annotations

import json

from typeforce.errors import TypeforceError


class JsonFormatter:
    """Format errors as a JSON array."""

    def format(self, errors: list[TypeforceError]) -> str:
        """Return a JSON string representing the list of errors."""
        payload = [
            {
                "file": error.file,
                "line": error.line,
                "col": error.col,
                "code": error.code,
                "message": error.message,
            }
            for error in errors
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False)
