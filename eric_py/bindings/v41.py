"""ERiC 41.x specific ctypes structures."""

from __future__ import annotations

import ctypes
from ..types import EricPdfCallback, EricZertifikatHandle

class eric_druck_parameter_t(ctypes.Structure):
    """See eric_druck_parameter_t in eric_types.h (version must be 4)."""

    _fields_ = [
        ("version", ctypes.c_uint32),
        ("vorschau", ctypes.c_uint32),
        ("ersteSeite", ctypes.c_uint32),
        ("duplexDruck", ctypes.c_uint32),
        ("pdfName", ctypes.c_char_p),
        ("fussText", ctypes.c_char_p),
        ("pdfCallback", EricPdfCallback),
        ("pdfCallbackBenutzerdaten", ctypes.c_void_p),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = 4


class eric_verschluesselungs_parameter_t(ctypes.Structure):
    """See eric_verschluesselungs_parameter_t in eric_types.h (version must be 3)."""

    _fields_ = [
        ("pin", ctypes.c_char_p),
        ("version", ctypes.c_uint32),
        ("zertifikatHandle", EricZertifikatHandle),
        ("abrufCode", ctypes.c_char_p),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = 3
