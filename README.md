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

## Development

Install dev dependencies and run tests:

```bash
pip install -e .[dev]
pytest
```
