"""High-level helper functions to drive ERiC workflows."""

from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import api
from .errors import check_eric_result
from .loader import EricLibraryLoadError, eric_plugin_path
from .versioning import (
    DEFAULT_ERIC_VERSION,
    EricVersionConfig,
    SUPPORTED_ERIC_VERSIONS,
    VERSION_CONFIGS,
    detect_eric_version,
)
from .types import (
    EricBearbeitungFlag,
    EricPdfCallback,
    EricTransferHandle,
    EricZertifikatHandle,
    eric_druck_parameter_t,
    eric_verschluesselungs_parameter_t,
)


@dataclass
class EricResult:
    """Container for ERiC responses."""

    code: int
    validation_response: str
    server_response: str
    transfer_handle: Optional[int] = None


class EricClient:
    """Context-managed ERiC client for single-threaded workflows."""

    def __init__(
        self,
        eric_home: Optional[os.PathLike[str] | str] = None,
        log_dir: Optional[os.PathLike[str] | str] = None,
        eric_version: Optional[str] = None,
    ):
        self.eric_home = Path(eric_home) if eric_home else eric_plugin_path()
        self.log_dir = Path(log_dir) if log_dir else Path.cwd()
        self._initialized = False
        # Detect ERiC version from installation path, then merge with explicit
        # selection and environment expectations.
        detected_version = detect_eric_version(self.eric_home)
        self.detected_eric_version: Optional[str] = detected_version

        # Start from explicit version (if provided), otherwise auto-detected,
        # otherwise fall back to the default supported version.
        version_key = eric_version or detected_version or DEFAULT_ERIC_VERSION

        expected_env = os.environ.get("ERIC_EXPECTED_VERSION")
        policy = os.environ.get("ERIC_VERSION_POLICY", "warn").lower()

        def _handle_mismatch(msg: str) -> None:
            if policy == "strict":
                raise EricLibraryLoadError(msg)
            if policy == "warn":
                print(f"[eric-py] WARNING: {msg}")

        if expected_env and version_key != expected_env:
            _handle_mismatch(
                f"Configured ERiC version '{version_key}' does not match "
                f"ERIC_EXPECTED_VERSION='{expected_env}'."
            )

        if detected_version and detected_version != version_key:
            _handle_mismatch(
                f"Auto-detected ERiC version '{detected_version}' from "
                f"path {self.eric_home} differs from configured '{version_key}'."
            )

        if version_key not in SUPPORTED_ERIC_VERSIONS:
            _handle_mismatch(
                f"ERiC version '{version_key}' is not in supported set "
                f"{SUPPORTED_ERIC_VERSIONS}."
            )

        # Configuration for the selected ERiC version (struct versions etc.).
        self.version_config: EricVersionConfig = VERSION_CONFIGS.get(
            version_key,
            VERSION_CONFIGS[DEFAULT_ERIC_VERSION],
        )

    def __enter__(self) -> "EricClient":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def initialize(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        rc = api.init_eric(self.eric_home, self.log_dir)
        check_eric_result(rc, api.get_error_text(rc))
        self._initialized = True

    def close(self) -> None:
        if not self._initialized:
            return
        rc = api.shutdown_eric()
        check_eric_result(rc, api.get_error_text(rc))
        self._initialized = False

    def _build_print_params(self, pdf_path: Optional[Path], preview: bool) -> Optional[eric_druck_parameter_t]:
        if pdf_path is None:
            return None
        params = eric_druck_parameter_t()
        params.vorschau = 1 if preview else 0
        params.ersteSeite = 0
        params.duplexDruck = 0
        params.pdfName = str(pdf_path).encode("utf-8")
        params.fussText = None
        params.pdfCallback = EricPdfCallback()
        params.pdfCallbackBenutzerdaten = None
        return params

    def _build_crypto_params(self, cert_handle: EricZertifikatHandle, pin: Optional[str]) -> eric_verschluesselungs_parameter_t:
        params = eric_verschluesselungs_parameter_t()
        params.zertifikatHandle = cert_handle
        params.pin = pin.encode("utf-8") if pin is not None else None
        params.abrufCode = None
        return params

    def validate_xml(self, xml_text: str, datenart_version: str, pdf_path: Optional[os.PathLike[str] | str] = None) -> EricResult:
        print_params_struct = self._build_print_params(Path(pdf_path) if pdf_path else None, preview=True)
        flags = EricBearbeitungFlag.ERIC_VALIDIERE
        if print_params_struct is not None:
            flags |= EricBearbeitungFlag.ERIC_DRUCKE
        return self._process(
            xml_text=xml_text,
            datenart_version=datenart_version,
            flags=flags,
            print_params=print_params_struct,
            crypto_params=None,
            transfer_handle=None,
        )

    def send_xml(
        self,
        xml_text: str,
        datenart_version: str,
        certificate_path: os.PathLike[str] | str,
        pin: Optional[str],
        pdf_path: Optional[os.PathLike[str] | str] = None,
        transfer_handle: Optional[int] = None,
    ) -> EricResult:
        """Send XML with certificate-based authentication."""
        print_params_struct = self._build_print_params(Path(pdf_path) if pdf_path else None, preview=False)
        flags = EricBearbeitungFlag.ERIC_VALIDIERE | EricBearbeitungFlag.ERIC_SENDE
        if print_params_struct is not None:
            flags |= EricBearbeitungFlag.ERIC_DRUCKE

        cert_handle, info_pin_support = self._load_certificate(Path(certificate_path), pin)
        try:
            crypto_params_struct = self._build_crypto_params(cert_handle, pin)
            result = self._process(
                xml_text=xml_text,
                datenart_version=datenart_version,
                flags=flags,
                print_params=print_params_struct,
                crypto_params=crypto_params_struct,
                transfer_handle=transfer_handle,
            )
        finally:
            api.EricCloseHandleToCertificate(cert_handle)
        return result

    def _load_certificate(self, cert_path: Path, pin: Optional[str]) -> tuple[EricZertifikatHandle, int]:
        handle = EricZertifikatHandle()
        info_pin = ctypes.c_uint32()
        rc = api.EricGetHandleToCertificate(
            ctypes.byref(handle),
            ctypes.byref(info_pin),
            str(cert_path).encode("utf-8"),
            pin.encode("utf-8") if pin is not None else None,
        )
        check_eric_result(rc, api.get_error_text(rc))
        return handle, info_pin.value

    def _process(
        self,
        xml_text: str,
        datenart_version: str,
        flags: int,
        print_params: Optional[eric_druck_parameter_t],
        crypto_params: Optional[eric_verschluesselungs_parameter_t],
        transfer_handle: Optional[int],
    ) -> EricResult:
        xml_bytes = xml_text.encode("utf-8")
        dav_bytes = datenart_version.encode("utf-8")

        response_buffer = api.create_buffer()
        server_buffer = api.create_buffer()
        transfer_holder = EricTransferHandle(transfer_handle or 0) if transfer_handle is not None else None
        transfer = ctypes.pointer(transfer_holder) if transfer_holder is not None else None

        try:
            rc = api.EricBearbeiteVorgang(
                xml_bytes,
                dav_bytes,
                ctypes.c_uint32(flags),
                ctypes.byref(print_params) if print_params else None,
                ctypes.byref(crypto_params) if crypto_params else None,
                transfer,
                response_buffer,
                server_buffer,
            )
            error_text = api.get_error_text(rc)
            check_eric_result(rc, error_text)

            validation_response = api.read_buffer(response_buffer).decode("utf-8", errors="replace")
            server_response = api.read_buffer(server_buffer).decode("utf-8", errors="replace")
            transfer_value = transfer.contents.value if transfer is not None else None
            return EricResult(
                code=rc,
                validation_response=validation_response,
                server_response=server_response,
                transfer_handle=transfer_value,
            )
        finally:
            api.free_buffer(response_buffer)
            api.free_buffer(server_buffer)
