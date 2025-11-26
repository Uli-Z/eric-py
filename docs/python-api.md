# eric-py Python API Overview

This document describes the main entry points of the `eric-py` package and how
they relate to the underlying ERiC API.

The focus is on:

- high-level helpers (`EricClient`, `EricResult`),
- environment and configuration handling,
- and selected low-level bindings that are safe to call directly.

For detailed semantics of the ERiC functions themselves, always refer to the
official ERiC documentation from the ELSTER developer portal.

## Getting started

This section shows a minimal end-to-end example using `EricClient` to
validate an XML document with ERiC.

1. Install ERiC and set `ERIC_HOME`:

   ```bash
   export ERIC_HOME=/path/to/ERiC-41.6.2.0/Linux-x86_64
   ```

2. Install `eric-py` in your virtual environment:

   ```bash
   pip install eric-py
   ```

3. Validate an XML document:

   ```python
   from pathlib import Path

   from eric_py.errors import EricError
   from eric_py.facade import EricClient


   def validate_example(xml_path: str, datenart_version: str) -> None:
       xml_text = Path(xml_path).read_text(encoding="utf-8")

       try:
           with EricClient() as client:
               result = client.validate_xml(xml_text, datenart_version=datenart_version)
           print(f"ERiC return code: {result.code}")
           print("Validation response:")
           print(result.validation_response)
           if result.server_response:
               print("Server response:")
               print(result.server_response)
       except EricError as exc:
           print(f"Validation failed: {exc}")
   ```

4. Call the helper with a suitable XML and `datenartVersion`, for example:

   ```python
   validate_example("ESt_2020-Beispiel_Loesung.xml", "ESt_2020")
   ```

This mirrors the flow in the official ERiC tutorial and the `ericdemo`
examples, but uses the Python wrapper instead of C++ or Java.

## High-level API: `eric_py.facade`

### `EricClient`

```python
from eric_py.facade import EricClient
```

Context-managed client for single-threaded ERiC workflows. It handles:

- initialization and shutdown (`EricInitialisiere` / `EricBeende`),
- optional log directory management,
- building print and crypto parameter structures,
- invoking `EricBearbeiteVorgang` for validation and send flows.

**Constructor**

```python
EricClient(
    eric_home: os.PathLike[str] | str | None = None,
    log_dir: os.PathLike[str] | str | None = None,
    eric_version: str | None = None,
)
```

- `eric_home`:
  - optional override for the ERiC installation directory.
  - if omitted, `eric_py.loader.eric_plugin_path()` is used, which in turn
    resolves from `ERIC_HOME` or a repository-specific default.
- `log_dir`:
  - directory where ERiC log files are written.
  - defaults to the current working directory.
- `eric_version`:
  - optional explicit ERiC version string (e.g. `"41.6.2.0"`), otherwise
    auto-detected from the ERiC path or taken from the default configuration.

`EricClient` can also be used as a context manager:

```python
with EricClient() as client:
    ...
```

This ensures that ERiC is properly initialized and shut down.

**Methods**

- `validate_xml(xml_text: str, datenart_version: str, pdf_path: os.PathLike[str] | str | None = None) -> EricResult`

  Validate an XML document with ERiC without sending it.

  - `xml_text` – XML payload as UTF‑8 string.
  - `datenart_version` – ERiC `datenartVersion` (e.g. `"ESt_2020"`, `"Bilanz_6.5"`).
  - `pdf_path` – optional path for a preview PDF; if provided, ERiC is configured
    to generate a PDF and write it to this path.

- `send_xml(xml_text: str, datenart_version: str, certificate_path: os.PathLike[str] | str, pin: str | None, pdf_path: os.PathLike[str] | str | None = None, transfer_handle: int | None = None) -> EricResult`

  Validate and send an XML document using a certificate.

  - `certificate_path` – path to a PFX/PSE file.
  - `pin` – PIN/password for the certificate (ASCII only, see ERiC docs).
  - `pdf_path` – optional confirmation PDF path.
  - `transfer_handle` – optional existing transfer handle for follow-up calls.

  This method will:

  - obtain a certificate handle via `EricGetHandleToCertificate`,
  - build the encryption parameters,
  - call `EricBearbeiteVorgang` with `ERIC_VALIDIERE` and `ERIC_SENDE` flags,
  - and close the certificate handle afterwards.

### `EricResult`

```python
from eric_py.facade import EricResult
```

Lightweight container for ERiC responses:

- `code: int` – ERiC return code.
- `validation_response: str` – XML string from the validation buffer.
- `server_response: str` – XML string from the server response buffer.
- `transfer_handle: int | None` – transfer handle for follow-up operations.

## Error handling: `eric_py.errors`

### `EricError`

```python
from eric_py.errors import EricError
```

Exception type raised when ERiC returns an error code via the high-level
facade or when `check_eric_result` is used.

Attributes:

- `code: int` – ERiC return code.
- `message: str | None` – optional error message (typically from
  `EricHoleFehlerText`).

### `check_eric_result(code: int, message: str | None = None) -> None`

Raises `EricError` if `code` is not `EricErrorCode.ERIC_OK`.

Typical usage:

```python
from eric_py.errors import check_eric_result
from eric_py.types import EricErrorCode

rc = some_eric_call(...)
check_eric_result(rc, "optional context message")
```

## Types and enums: `eric_py.types`

This module defines:

- `EricErrorCode` – a subset of ERiC error codes (`eric_fehlercodes.h`),
- `EricBearbeitungFlag` – bit flags for `EricBearbeiteVorgang`,
- struct types:
  - `eric_druck_parameter_t`
  - `eric_verschluesselungs_parameter_t`
  - `eric_zertifikat_parameter_t`
- callback prototypes:
  - `EricPdfCallback`
  - `EricLogCallback`
  - `EricFortschrittCallback`

These definitions mirror the C structs and enums documented in
`eric_types.h` and related headers. Their layout is chosen to match
ERiC 41.6.2.0 and may need updates for future ERiC releases.

## Loader: `eric_py.loader`

Helpers for locating and loading ERiC shared libraries:

- `eric_plugin_path(eric_home: os.PathLike[str] | str | None = None) -> Path`
  - Resolves the ERiC home directory.
  - Resolution order:
    1. explicit `eric_home` argument,
    2. `ERIC_HOME` environment variable.
  - Raises `EricLibraryLoadError` if no suitable path can be determined.

- `load_ericapi(eric_home: os.PathLike[str] | str | None = None) -> ctypes.CDLL`
  - Loads `libericapi.so` from `<ERiC_HOME>/lib`.

- `load_erictoolkit(eric_home: os.PathLike[str] | str | None = None) -> ctypes.CDLL`
  - Loads `liberictoolkit.so` from `<ERiC_HOME>/erictoolkit`.

- `EricLibraryLoadError(RuntimeError)`
  - Raised when a shared library cannot be found or loaded.

## Low-level API: `eric_py.api`

The `eric_py.api` module exposes thin `ctypes` bindings for selected ERiC
functions. These are considered a low-level API: their signatures follow
the C declarations closely and may be extended over time.

Currently bound functions include (non-exhaustive):

- `EricInitialisiere(plugin_path: bytes, log_path: bytes) -> int`
- `EricBeende() -> int`
- `EricBearbeiteVorgang(...) -> int`
- `EricCheckXML(xml: bytes, datenart_version: bytes, fehlertext_puffer: EricRueckgabepufferHandle) -> int`
- `EricHoleFehlerText(code: int, puffer: EricRueckgabepufferHandle) -> int`
- `EricRueckgabepufferErzeugen() -> EricRueckgabepufferHandle`
- `EricRueckgabepufferFreigeben(handle: EricRueckgabepufferHandle) -> int`
- `EricRueckgabepufferInhalt(handle: EricRueckgabepufferHandle) -> ctypes.c_char_p`
- `EricRueckgabepufferLaenge(handle: EricRueckgabepufferHandle) -> ctypes.c_uint32`
- `EricGetHandleToCertificate(...) -> int`
- `EricCloseHandleToCertificate(handle: EricZertifikatHandle) -> int`
- `EricHoleZertifikatEigenschaften(...) -> int`
- `EricRegistriereLogCallback(...) -> int`
- `EricRegistriereFortschrittCallback(...) -> int`
- `EricHoleTestfinanzaemter(puffer: EricRueckgabepufferHandle) -> int`

Utility helpers:

- `create_buffer() -> EricRueckgabepufferHandle`
- `free_buffer(handle: EricRueckgabepufferHandle) -> None`
- `read_buffer(handle: EricRueckgabepufferHandle) -> bytes`
- `get_error_text(code: int) -> str | None`
- `init_eric(plugin_path: Path, log_path: Path) -> int`
- `shutdown_eric() -> int`

Use these functions if you need finer control than `EricClient` provides,
but be prepared to handle raw error codes and memory buffers.

## Versioning: `eric_py.versioning`

This module centralizes knowledge about supported ERiC versions and related
struct settings.

Key elements:

- `EricVersionConfig`

  ```python
  from dataclasses import dataclass

  @dataclass(frozen=True)
  class EricVersionConfig:
      eric_version: str
      druck_param_version: int
      crypto_param_version: int
  ```

- `SUPPORTED_ERIC_VERSIONS: tuple[str, ...]`
  - Tuple of ERiC versions that this `eric-py` release officially supports.

- `DEFAULT_ERIC_VERSION: str`
  - Default ERiC version used when no explicit version is configured.

- `VERSION_CONFIGS: dict[str, EricVersionConfig]`
  - Map from version string to configuration object.

- `is_supported_version(version: str) -> bool`
- `list_supported_versions() -> Iterable[str]`
- `detect_eric_version(eric_home: os.PathLike[str] | str) -> str | None`
  - Attempts to extract a version string from the ERiC installation path
    (e.g. `ERiC-41.6.2.0/Linux-x86_64`).

`EricClient` uses these helpers to derive `self.version_config` based on the
installation path, optional `eric_version`, and environment expectations.

## Environment variables

The following environment variables influence `eric-py` behaviour:

- `ERIC_HOME`:
  - Required for locating the ERiC installation unless an explicit `eric_home`
    path is provided.
- `ERIC_EXPECTED_VERSION` (optional):
  - Expected ERiC version string (e.g. `"41.6.2.0"`). Mismatches are handled
    according to `ERIC_VERSION_POLICY`.
- `ERIC_VERSION_POLICY` (optional):
  - One of:
    - `"strict"` – mismatches raise `EricLibraryLoadError`.
    - `"warn"` (default) – mismatches print a warning.
    - `"ignore"` – mismatches are silently ignored.
- `ERIC_LOG_DIR` (optional, future use):
  - Target directory for logs; if unset, `EricClient` uses the provided
    `log_dir` argument or the current working directory.

For testing and examples, additional environment variables such as
`ERIC_EXAMPLE_XML`, `ERIC_EXAMPLE_DAV`, and `ERIC_TUTORIAL_EXAMPLES` are
used; see the main `README.md` for details.
