"""ERiC version support and configuration helpers."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple


@dataclass(frozen=True)
class EricVersionConfig:
    """Configuration for a specific ERiC version family."""

    eric_version: str
    druck_param_version: int
    crypto_param_version: int


# Officially supported ERiC versions for this eric-py release.
SUPPORTED_ERIC_VERSIONS: Tuple[str, ...] = (
    "41.6.2.0",
)

# Default ERiC version if none is specified explicitly.
DEFAULT_ERIC_VERSION: str = SUPPORTED_ERIC_VERSIONS[0]

# Per-version configuration map. Extend this as new versions are validated.
VERSION_CONFIGS: Dict[str, EricVersionConfig] = {
    "41.6.2.0": EricVersionConfig(
        eric_version="41.6.2.0",
        druck_param_version=4,
        crypto_param_version=3,
    ),
}


def is_supported_version(version: str) -> bool:
    """Return True if the given ERiC version string is officially supported."""
    return version in SUPPORTED_ERIC_VERSIONS


def list_supported_versions() -> Iterable[str]:
    """Return an iterable of supported ERiC version strings."""
    return SUPPORTED_ERIC_VERSIONS


def detect_eric_version(eric_home: os.PathLike[str] | str) -> Optional[str]:
    """
    Try to detect the ERiC version based on the ERIC_HOME path.

    We do not rely on documentation files (which may not be shipped together
    with the runtime). Instead, we look for a version pattern in the names of
    the ERIC_HOME directory and its parents, for example::

        /opt/ERiC-41.6.2.0/Linux-x86_64
        /opt/eric/41.6.2.0/Linux-x86_64

    Any path component that contains a substring matching ``\\d+.\\d+.\\d+.\\d+``
    is treated as the version string (e.g. ``41.6.2.0``). If no such component
    is found, the function returns ``None``.
    """
    home = Path(eric_home).expanduser().resolve()
    pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)")

    current: Optional[Path] = home
    while current is not None and current != current.parent:
        match = pattern.search(current.name)
        if match:
            return match.group(1)
        current = current.parent

    return None
