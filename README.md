# eric-py

Python bindings and helpers for ERiC (ELSTER Rich Client).

This library provides:
- `ctypes` bindings for `libericapi.so` and related ERiC libraries.
- High-level helpers for initializing ERiC and running validation / send workflows.
- A small error and type layer (`EricError`, `EricErrorCode`, etc.).

The ERiC binaries and header files are **not** included in this repository.
You must install the official ERiC distribution yourself and point `eric-py`
to it via environment variables (see below).

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
from eric.facade import EricClient

with EricClient() as client:
    result = client.validate_xml("<YourXML/>", "ESt_2020")
    print(result.validation_response)
```

For lower-level control you can import from `eric.api`, `eric.types`, and `eric.errors`.

## Configuration

`eric-py` never ships ERiC itself. You must obtain ERiC from the official
source and configure its location via environment variables:

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
from eric.facade import EricClient

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
