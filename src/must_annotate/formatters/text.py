"""Human-readable text formatter."""
from __future__ import annotations

from must_annotate.errors import MustAnnotateError
from must_annotate.formatters.base import BaseFormatter


class TextFormatter(BaseFormatter):
    """Format errors for terminal output."""

    def format(self, errors: list[MustAnnotateError]) -> str:
        """Return a multi-line string suitable for terminal display."""
        if not errors:
            return "No errors found."

        lines: list[str] = [str(error) for error in errors]

        file_count = len({error.file for error in errors})
        error_word = "error" if len(errors) == 1 else "errors"
        file_word = "file" if file_count == 1 else "files"
        summary = f"\nFound {len(errors)} {error_word} in {file_count} {file_word}"
        lines.append(summary)

        return "\n".join(lines)
