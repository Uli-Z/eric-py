# eric-py

**Status: early-stage draft.**  
This project is a quickly assembled, minimally reviewed prototype of Python
bindings for ERiC. While a fair amount of time and care has already gone into
its design and tests, it should still be considered experimental. It is shared
in the hope that it is useful to others, but without any guarantees.

`eric-py` started as an automated port of key ideas and APIs from the Rust
project [`eric-rs`](https://github.com/quambene/eric-rs), using agentic-coding
workflows with OpenAI GPT 5.1, followed by manual review and adaptation.

Python bindings and helpers for ERiC (ELSTER Rich Client).

This library provides:
- `ctypes` bindings for `libericapi.so` and related ERiC libraries.
- High-level helpers for initializing ERiC and running validation / send workflows.
- A small error and type layer (`EricError`, `EricErrorCode`, etc.).

The ERiC binaries and header files are **not** included in this repository.
You must obtain the official ERiC distribution yourself (for example from the
ELSTER developer portal) and point `eric-py` to it via environment variables
and/or configuration (see below).

## Installation

1. Install the ERiC distribution (e.g. `ERiC/Linux-x86_64`) on your system.
2. Set the `ERIC_HOME` environment variable to the ERiC root directory.
3. Install `eric-py` in a virtual environment:

```bash
pip install -e .
```

## Credits

`eric-py` is inspired by and conceptually derived from the Rust project
[`eric-rs`](https://github.com/quambene/eric-rs). The FFI design and
several data structures follow the patterns established there, adapted
and extended for Python.

## Usage

After installation you can use the high-level facade:

```python
from eric_py.facade import EricClient

with EricClient() as client:
    result = client.validate_xml("<YourXML/>", "ESt_2020")
    print(result.validation_response)
```

For lower-level control you can import from `eric_py.api`, `eric_py.types`, and `eric_py.errors`.

An executable walking-skeleton example is provided in `examples/m2a_walking_skeleton.py`.
It expects:

- `ERIC_EXAMPLE_XML`: path to an XML file to validate
- optional `ERIC_EXAMPLE_DAV`: ERiC datenartVersion string (default `Bilanz_6.5`)

For a more detailed description of the available Python API, see
`docs/python-api.md` in this repository.

## Configuration

`eric-py` never ships ERiC itself. You must obtain ERiC from the official
ELSTER developer resources and configure its location via environment
variables:

- `ERIC_HOME` (required): absolute path to the ERiC root directory that
  contains `lib/libericapi.so` and `erictoolkit/liberictoolkit.so`.
  Example: `/opt/ERiC/Linux-x86_64`.
- `ERIC_LOG_DIR` (optional, future use): directory where ERiC log files
  should be written. If not set, the current working directory is used
  by the high-level facade.

The loader uses the following resolution order:

1. An explicit `eric_home` argument passed to loader functions or `EricClient`.
2. The `ERIC_HOME` environment variable.

If neither is set, an `EricLibraryLoadError` is raised with a detailed hint.

## Supported ERiC versions

For this release, `eric-py` is developed and tested against the following
ERiC version(s):

- `41.6.2.0`

The Python API supports selecting different ERiC installations by path:

```python
from eric_py.facade import EricClient

with EricClient(eric_home="/opt/eric/41.6.2.0/Linux-x86_64") as client:
    ...
```

Future releases may extend the list of supported versions. If you point
`ERIC_HOME` to a different ERiC version, you should run your own tests to
verify compatibility for your use case.

## Development

Install dev dependencies and run tests:

```bash
pip install -e .[dev]
pytest
```

### Testing with a local ERiC distribution

For integration tests, place the official ERiC distribution alongside this
repository and/or point `ERIC_HOME` to it.
One recommended layout for ERiC 41.6.2.0 is:

```text
/path/to/workspace/
  ERiC-41.6.2.0/
    Linux-x86_64/
      lib/libericapi.so
      erictoolkit/liberictoolkit.so
  eric-py/
    ...
```

If `ERIC_HOME` is not set, the test suite will automatically use
`../ERiC-41.6.2.0/Linux-x86_64` relative to the repository root when present.

Sending XML to ELSTER is not executed by default. To opt into send tests,
you must provide credentials and explicitly enable them:

- `ERIC_TEST_ENABLE_SEND=1`
- `CERTIFICATE_PATH` and `CERTIFICATE_PASSWORD` for your certificate
- `ERIC_EXAMPLE_XML` pointing to a suitable XML document
- optional `ERIC_EXAMPLE_DAV` for the ERiC `datenartVersion`

Without these variables, send-related tests are skipped; only local
initialization and validation flows are exercised.

You can also optionally validate the official ESt_2020 tutorial example XML
by pointing `ERIC_TUTORIAL_EXAMPLES` to the directory containing the ERiC
Tutorial example files (for example, `Dokumentation/Tutorial/Beispiele` from
the ERiC distribution). In this case, a dedicated test will invoke
`EricCheckXML` on `ESt_2020-Beispiel_Loesung.xml` without asserting any
specific return code.

## Disclaimer

This software is provided on a best-effort, experimental basis only.
It does not constitute legal, tax, or professional advice. Use it at
your own risk. The author (Ulrich Zorn) and contributors assume no
responsibility or liability for any errors, data loss, financial damage,
or other consequences arising from the use of this project.

## Provenance

Large parts of this repository (project scaffolding, FFI bindings and
documentation text) were created and iterated on using agentic-coding
tools (OpenAI GPT 5.1), under the guidance and review of the maintainer
[@Uli-Z](https://github.com/Uli-Z).
