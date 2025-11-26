"""Walking skeleton for ERiC validation using eric-py."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repository root is importable when running this example directly.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eric_py.errors import EricError  # noqa: E402
from eric_py.facade import EricClient  # noqa: E402


def resolve_example_xml() -> Path:
    """
    Try to find an example XML to validate.

    By default this function expects the caller to provide the path via the
    environment variable ``ERIC_EXAMPLE_XML``. This keeps eric-py free from
    shipping any tax or ERiC-specific XML fixtures.
    """
    env_path = os.environ.get("ERIC_EXAMPLE_XML")
    if not env_path:
        raise SystemExit(
            "Please set ERIC_EXAMPLE_XML to the path of an XML file "
            "to validate with ERiC."
        )
    xml_path = Path(env_path).expanduser()
    if not xml_path.exists():
        raise SystemExit(f"Example XML file not found: {xml_path}")
    return xml_path


def main() -> int:
    xml_path = resolve_example_xml()
    datenart_version = os.environ.get("ERIC_EXAMPLE_DAV", "Bilanz_6.5")

    xml_text = xml_path.read_text(encoding="utf-8")
    # Replace the placeholder Hersteller-ID with a neutral value for validation-only runs.
    xml_text = xml_text.replace("<HerstellerID>74931</HerstellerID>", "<HerstellerID>00000</HerstellerID>")

    try:
        with EricClient() as client:
            result = client.validate_xml(xml_text, datenart_version=datenart_version)
            print(f"Validation return code: {result.code}")
            print("Validation response:")
            print(result.validation_response)
            if result.server_response:
                print("Server response:")
                print(result.server_response)
        return 0
    except EricError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
