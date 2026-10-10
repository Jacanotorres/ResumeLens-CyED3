"""Stage 4 - validate candidate profile DSL text against the textX grammar."""

from functools import lru_cache
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError

GRAMMAR_PATH = Path(__file__).with_name("candidate.tx")


class DSLValidationError(ValueError):
    """Raised when DSL text breaks the lexical or syntactic rules of the grammar."""


@lru_cache(maxsize=1)
def _metamodel():
    return metamodel_from_file(str(GRAMMAR_PATH))


def validate(text):
    """Parse DSL text and return the textX model.

    Raises DSLValidationError (with line and column) if the text is invalid.
    """
    try:
        return _metamodel().model_from_str(text)
    except TextXSyntaxError as exc:
        raise DSLValidationError(f"line {exc.line}, column {exc.col}: {exc.message}") from exc