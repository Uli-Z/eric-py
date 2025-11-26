"""Locate and load ERiC shared libraries via ctypes."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
from typing import Optional


class EricLibraryLoadError(RuntimeError):
    """Raised when an ERiC shared library cannot be loaded."""


def _resolve_home(eric_home: Optional[os.PathLike[str] | str]) -> Path:
    """
    Resolve the ERiC home directory.

    Resolution order:
    - explicit ``eric_home`` argument, if given
    - ``ERIC_HOME`` environment variable

    No default inside the package is used to avoid accidentally bundling
    or relying on ERiC binaries inside the repository.
    """
    env_home = os.environ.get("ERIC_HOME")
    if eric_home is None and env_home is None:
        raise EricLibraryLoadError(
            "ERIC_HOME is not set and no eric_home override was provided. "
            "Install the official ERiC distribution separately and point "
            "ERIC_HOME to its root directory (e.g. /opt/eric/Linux-x86_64)."
        )

    base = Path(eric_home or env_home).expanduser().resolve()
    return base


def _load_shared_library(path: Path) -> ctypes.CDLL:
    if not path.exists():
        raise EricLibraryLoadError(
            f"Expected ERiC library at {path} but it does not exist. "
            "Set ERIC_HOME to the root of the ERiC Linux-x86_64 distribution."
        )
    try:
        # RTLD_GLOBAL is required so dependent libs/plugins can resolve symbols.
        return ctypes.CDLL(str(path), mode=ctypes.RTLD_GLOBAL)
    except OSError as exc:
        raise EricLibraryLoadError(
            f"Failed to load ERiC library at {path}: {exc}. "
            "Ensure dependent libraries are available (libericxerces, plugins)."
        ) from exc


def load_ericapi(eric_home: Optional[os.PathLike[str] | str] = None) -> ctypes.CDLL:
    """Load libericapi.so using the provided ERiC home or ERIC_HOME env."""
    home = _resolve_home(eric_home)
    lib_path = home / "lib" / "libericapi.so"
    return _load_shared_library(lib_path)


def load_erictoolkit(eric_home: Optional[os.PathLike[str] | str] = None) -> ctypes.CDLL:
    """Load liberictoolkit.so using the provided ERiC home or ERIC_HOME env."""
    home = _resolve_home(eric_home)
    lib_path = home / "erictoolkit" / "liberictoolkit.so"
    return _load_shared_library(lib_path)


def eric_plugin_path(eric_home: Optional[os.PathLike[str] | str] = None) -> Path:
    """Return the plugin search path passed to EricInitialisiere."""
    return _resolve_home(eric_home)
