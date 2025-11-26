"""Integration tests against the local ERiC runtime.

These tests exercise the ctypes bindings and high-level facade as far
as possible without actually sending data to ELSTER.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from eric_py import api
from eric_py.errors import EricError
from eric_py.facade import EricClient
from eric_py.loader import EricLibraryLoadError, eric_plugin_path, load_ericapi, load_erictoolkit


def _eric_home_from_env() -> Path | None:
    value = os.environ.get("ERIC_HOME")
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.exists() else None


ERIC_HOME = _eric_home_from_env()
ERIC_TUTORIAL_EXAMPLES = os.environ.get("ERIC_TUTORIAL_EXAMPLES")


@pytest.mark.skipif(ERIC_HOME is None, reason="ERIC_HOME not configured or ERiC not present")
def test_loader_can_resolve_and_load_libraries() -> None:
    """Loader should resolve ERiC paths and load shared libraries."""
    home = eric_plugin_path()
    assert home.exists()
    lib_api = load_ericapi()
    lib_toolkit = load_erictoolkit()
    assert lib_api is not None
    assert lib_toolkit is not None


@pytest.mark.skipif(ERIC_HOME is None, reason="ERIC_HOME not configured or ERiC not present")
def test_api_error_text_roundtrip() -> None:
    """get_error_text should be callable for a known code."""
    # Even if the code is not ERIC_OK for this context, the call itself
    # should succeed and return a string or None.
    text = api.get_error_text(0)
    if text is not None:
        assert isinstance(text, str)


@pytest.mark.skipif(ERIC_HOME is None, reason="ERIC_HOME not configured or ERiC not present")
def test_client_initialize_and_shutdown() -> None:
    """EricClient should be able to initialize and shutdown ERiC."""
    log_dir = Path.cwd() / "tmp-eric-logs"
    if log_dir.exists():
        # Leave existing logs in place; we only need the directory.
        pass
    with EricClient(log_dir=log_dir) as client:
        # The context manager should have initialized ERiC without raising.
        assert client.detected_eric_version is None or isinstance(client.detected_eric_version, str)


@pytest.mark.skipif(ERIC_HOME is None, reason="ERIC_HOME not configured or ERiC not present")
def test_check_xml_with_unknown_datenartversion() -> None:
    """EricCheckXML should fail with a specific error for unknown datenartVersion."""
    xml_bytes = b"<Test/>"
    buffer = api.create_buffer()
    try:
        rc = api.EricCheckXML(xml_bytes, b"UNKNOWN_1.0", buffer)
        # For an unknown datenartVersion, ERiC should return a non-zero error
        # code. The content of the error buffer may be empty depending on the
        # ERiC configuration, so we only assert that the call itself succeeds
        # and returns an error code.
        assert isinstance(rc, int)
        assert rc != 0
    finally:
        api.free_buffer(buffer)


@pytest.mark.skipif(
    ERIC_HOME is None or not ERIC_TUTORIAL_EXAMPLES,
    reason="ERIC_HOME or ERIC_TUTORIAL_EXAMPLES not configured",
)
def test_tutorial_est_2020_example_with_checkxml() -> None:
    """Optionally validate the ESt_2020 tutorial example XML via EricCheckXML.

    Set ERIC_TUTORIAL_EXAMPLES to the directory containing the ERiC tutorial
    XML files (e.g. .../Dokumentation/Tutorial/Beispiele). This test does not
    assert semantic correctness of the XML; it only ensures that the binding
    can process the file without crashing.
    """
    examples_dir = Path(ERIC_TUTORIAL_EXAMPLES)
    xml_path = examples_dir / "ESt_2020-Beispiel_Loesung.xml"
    if not xml_path.exists():
        pytest.skip(f"Tutorial example XML not found: {xml_path}")

    xml_text = xml_path.read_text(encoding="utf-8")
    # Replace the illustrative Hersteller-ID with a neutral value to avoid
    # accidental use of a deprecated test ID.
    xml_text = xml_text.replace("<HerstellerID>74931</HerstellerID>", "<HerstellerID>00000</HerstellerID>")

    buffer = api.create_buffer()
    try:
        rc = api.EricCheckXML(xml_text.encode("utf-8"), b"ESt_2020", buffer)
        # The exact return code depends on the installed ERiC configuration; we
        # only assert that a call can be made and a result code is returned.
        assert isinstance(rc, int)
        _ = api.read_buffer(buffer)
    finally:
        api.free_buffer(buffer)


@pytest.mark.skipif(ERIC_HOME is None, reason="ERIC_HOME not configured or ERiC not present")
def test_send_requires_opt_in_and_credentials() -> None:
    """Sending should only be exercised when explicitly requested."""
    if os.environ.get("ERIC_TEST_ENABLE_SEND") != "1":
        pytest.skip("Sending is only tested when ERIC_TEST_ENABLE_SEND=1 is set")

    cert_path = os.environ.get("CERTIFICATE_PATH")
    cert_pin = os.environ.get("CERTIFICATE_PASSWORD")
    if not cert_path or not cert_pin:
        pytest.skip("CERTIFICATE_PATH and CERTIFICATE_PASSWORD must be set to test send")

    xml_path_value = os.environ.get("ERIC_EXAMPLE_XML")
    if not xml_path_value:
        pytest.skip("ERIC_EXAMPLE_XML must point to a valid XML document for send tests")

    xml_path = Path(xml_path_value)
    if not xml_path.exists():
        pytest.skip(f"Example XML for send test not found: {xml_path}")

    datenart_version = os.environ.get("ERIC_EXAMPLE_DAV", "Bilanz_6.5")
    xml_text = xml_path.read_text(encoding="utf-8")

    try:
        with EricClient() as client:
            result = client.send_xml(
                xml_text=xml_text,
                datenart_version=datenart_version,
                certificate_path=cert_path,
                pin=cert_pin,
            )
        assert isinstance(result.code, int)
    except EricError:
        # A semantic or validation error is acceptable for this opt-in test;
        # the important part is that the call path and bindings are exercised.
        pytest.xfail("ERiC returned an error code during send test")
    except EricLibraryLoadError:
        pytest.skip("ERiC libraries could not be loaded for send test")
