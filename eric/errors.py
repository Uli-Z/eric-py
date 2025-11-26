"""Error codes and exception types for ERiC interaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import EricErrorCode


@dataclass
class EricError(RuntimeError):
    """Raised when an ERiC API call returns an error code."""

    code: int
    message: Optional[str] = None

    def __str__(self) -> str:
        base = f"ERiC error {self.code}"
        if self.message:
            return f"{base}: {self.message}"
        return base


def check_eric_result(code: int, message: Optional[str] = None) -> None:
    """Raise EricError if the return code signals failure."""
    if code == EricErrorCode.ERIC_OK:
        return
    raise EricError(code=code, message=message)
