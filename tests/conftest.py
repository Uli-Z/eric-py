"""Pytest configuration for eric-py.

This module configures ERIC_HOME for tests so that the ERiC runtime
in the local checkout can be exercised without additional setup.
"""

from __future__ import annotations

import os
from pathlib import Path


def _candidate_eric_home() -> Path | None:
    """Return a default ERiC home if known, otherwise None."""
    repo_root = Path(__file__).resolve().parents[1]
    # Preferred layout: ERiC-41.6.2.0 next to this repository.
    candidate = repo_root.parent / "ERiC-41.6.2.0" / "Linux-x86_64"
    if candidate.exists():
        return candidate
    return None


def pytest_configure() -> None:
    """Set ERIC_HOME for tests if it is not provided by the environment."""
    if os.environ.get("ERIC_HOME"):
        return

    candidate = _candidate_eric_home()
    if candidate is not None:
        os.environ["ERIC_HOME"] = str(candidate)
