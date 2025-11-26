"""Low-level ERiC API bindings exposed via ctypes."""

from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Optional

from . import loader
from .types import (
    EricFortschrittCallback,
    EricLogCallback,
    EricRueckgabepufferHandle,
    EricTransferHandle,
    EricZertifikatHandle,
    eric_druck_parameter_t,
    eric_verschluesselungs_parameter_t,
)

# Load shared libraries once.
_ericapi = loader.load_ericapi()
_erictoolkit = loader.load_erictoolkit()

# ---------------------------------------------------------------------------
# Function bindings (single-thread API)

EricInitialisiere = _ericapi.EricInitialisiere
EricInitialisiere.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
EricInitialisiere.restype = ctypes.c_int

EricBeende = _ericapi.EricBeende
EricBeende.argtypes = []
EricBeende.restype = ctypes.c_int

EricBearbeiteVorgang = _ericapi.EricBearbeiteVorgang
EricBearbeiteVorgang.argtypes = [
    ctypes.c_char_p,  # datenpuffer
    ctypes.c_char_p,  # datenartVersion
    ctypes.c_uint32,  # bearbeitungsFlags
    ctypes.POINTER(eric_druck_parameter_t),  # druckParameter
    ctypes.POINTER(eric_verschluesselungs_parameter_t),  # cryptoParameter
    ctypes.POINTER(EricTransferHandle),  # transferHandle
    EricRueckgabepufferHandle,  # rueckgabeXmlPuffer
    EricRueckgabepufferHandle,  # serverantwortXmlPuffer
]
EricBearbeiteVorgang.restype = ctypes.c_int

EricCheckXML = _ericapi.EricCheckXML
EricCheckXML.argtypes = [
    ctypes.c_char_p,  # xml
    ctypes.c_char_p,  # datenartVersion
    EricRueckgabepufferHandle,  # fehlertextPuffer
]
EricCheckXML.restype = ctypes.c_int

EricHoleFehlerText = _ericapi.EricHoleFehlerText
EricHoleFehlerText.argtypes = [ctypes.c_int, EricRueckgabepufferHandle]
EricHoleFehlerText.restype = ctypes.c_int

EricRueckgabepufferErzeugen = _ericapi.EricRueckgabepufferErzeugen
EricRueckgabepufferErzeugen.argtypes = []
EricRueckgabepufferErzeugen.restype = EricRueckgabepufferHandle

EricRueckgabepufferFreigeben = _ericapi.EricRueckgabepufferFreigeben
EricRueckgabepufferFreigeben.argtypes = [EricRueckgabepufferHandle]
EricRueckgabepufferFreigeben.restype = ctypes.c_int

EricRueckgabepufferInhalt = _ericapi.EricRueckgabepufferInhalt
EricRueckgabepufferInhalt.argtypes = [EricRueckgabepufferHandle]
EricRueckgabepufferInhalt.restype = ctypes.c_char_p

EricRueckgabepufferLaenge = _ericapi.EricRueckgabepufferLaenge
EricRueckgabepufferLaenge.argtypes = [EricRueckgabepufferHandle]
EricRueckgabepufferLaenge.restype = ctypes.c_uint32

EricGetHandleToCertificate = _ericapi.EricGetHandleToCertificate
EricGetHandleToCertificate.argtypes = [
    ctypes.POINTER(EricZertifikatHandle),
    ctypes.POINTER(ctypes.c_uint32),  # iInfoPinSupport
    ctypes.c_char_p,  # psePath
    ctypes.c_char_p,  # pin
]
EricGetHandleToCertificate.restype = ctypes.c_int

EricCloseHandleToCertificate = _ericapi.EricCloseHandleToCertificate
EricCloseHandleToCertificate.argtypes = [EricZertifikatHandle]
EricCloseHandleToCertificate.restype = ctypes.c_int

EricHoleZertifikatEigenschaften = _ericapi.EricHoleZertifikatEigenschaften
EricHoleZertifikatEigenschaften.argtypes = [
    EricZertifikatHandle,
    ctypes.c_char_p,  # pin
    EricRueckgabepufferHandle,
]
EricHoleZertifikatEigenschaften.restype = ctypes.c_int

EricRegistriereLogCallback = _ericapi.EricRegistriereLogCallback
EricRegistriereLogCallback.argtypes = [
    EricLogCallback,
    ctypes.c_uint32,
    ctypes.c_void_p,
]
EricRegistriereLogCallback.restype = ctypes.c_int

EricRegistriereFortschrittCallback = _ericapi.EricRegistriereFortschrittCallback
EricRegistriereFortschrittCallback.argtypes = [
    EricFortschrittCallback,
    ctypes.c_void_p,
]
EricRegistriereFortschrittCallback.restype = ctypes.c_int

# ---------------------------------------------------------------------------
# Helper utilities


def create_buffer() -> EricRueckgabepufferHandle:
    return EricRueckgabepufferErzeugen()


def free_buffer(handle: EricRueckgabepufferHandle) -> None:
    if handle:
        EricRueckgabepufferFreigeben(handle)


def read_buffer(handle: EricRueckgabepufferHandle) -> bytes:
    """Read the content of a return buffer into bytes."""
    ptr = EricRueckgabepufferInhalt(handle)
    length = EricRueckgabepufferLaenge(handle)
    if not ptr or length == 0:
        return b""
    return ctypes.string_at(ptr, length)


def get_error_text(code: int) -> Optional[str]:
    """Retrieve the localized ERiC error text for a code, if available."""
    buffer = create_buffer()
    try:
        rc = EricHoleFehlerText(code, buffer)
        if rc != 0:
            return None
        content = read_buffer(buffer)
        return content.decode("utf-8", errors="replace")
    finally:
        free_buffer(buffer)


def init_eric(plugin_path: Path, log_path: Path) -> int:
    """Call EricInitialisiere with UTF-8 encoded paths."""
    return EricInitialisiere(
        str(plugin_path).encode("utf-8"),
        str(log_path).encode("utf-8"),
    )


def shutdown_eric() -> int:
    """Call EricBeende."""
    return EricBeende()
