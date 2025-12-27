"""ctypes definitions for ERiC structs and enums."""

from __future__ import annotations

import ctypes
import enum

# Handles and aliases
EricRueckgabepufferHandle = ctypes.c_void_p
EricZertifikatHandle = ctypes.c_uint32
EricTransferHandle = ctypes.c_uint32

# Callback prototypes
EricPdfCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint32,
    ctypes.c_void_p,
)
EricLogCallback = ctypes.CFUNCTYPE(
    None, ctypes.c_char_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_void_p
)
EricFortschrittCallback = ctypes.CFUNCTYPE(
    None, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p
)


class EricErrorCode(enum.IntEnum):
    """Subset of ERiC error codes; values come from eric_fehlercodes.h."""

    ERIC_OK = 0
    ERIC_GLOBAL_UNKNOWN = 610001001
    ERIC_GLOBAL_PRUEF_FEHLER = 610001002
    ERIC_GLOBAL_HINWEISE = 610001003
    ERIC_GLOBAL_ILLEGAL_STATE = 610001017
    ERIC_GLOBAL_DATENARTVERSION_UNBEKANNT = 610001042
    ERIC_GLOBAL_DATENARTVERSION_XML_INKONSISTENT = 610001044
    ERIC_GLOBAL_PUFFER_UNGLEICHER_INSTANZ = 610001050
    ERIC_GLOBAL_PUFFER_UEBERLAUF = 610001041
    ERIC_GLOBAL_STEUERNUMMER_UNGUELTIG = 610001034
    ERIC_GLOBAL_TRANSFERHANDLE_NICHT_INITIALISIERT = 610001078
    ERIC_GLOBAL_NICHT_GENUEGEND_ARBEITSSPEICHER = 610001013
    ERIC_GLOBAL_DATEI_NICHT_GEFUNDEN = 610001014


class EricBearbeitungFlag(enum.IntEnum):
    """Flags for EricBearbeiteVorgang (eric_bearbeitung_flag_t)."""

    ERIC_VALIDIERE = 1 << 1
    ERIC_SENDE = 1 << 2
    ERIC_DRUCKE = 1 << 5
    ERIC_PRUEFE_HINWEISE = 1 << 7
    ERIC_VALIDIERE_OHNE_FREIGABEDATUM = 1 << 8


class eric_zertifikat_parameter_t(ctypes.Structure):
    """Used for EricCreateKey (documented in eric_types.h, version must be 1)."""

    _fields_ = [
        ("version", ctypes.c_uint32),
        ("name", ctypes.c_char_p),
        ("land", ctypes.c_char_p),
        ("ort", ctypes.c_char_p),
        ("adresse", ctypes.c_char_p),
        ("email", ctypes.c_char_p),
        ("organisation", ctypes.c_char_p),
        ("abteilung", ctypes.c_char_p),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = 1
