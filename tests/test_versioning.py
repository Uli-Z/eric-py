"""Tests for ERiC versioning helpers."""

from eric.versioning import (
    DEFAULT_ERIC_VERSION,
    SUPPORTED_ERIC_VERSIONS,
    VERSION_CONFIGS,
    EricVersionConfig,
    is_supported_version,
    list_supported_versions,
)


def test_supported_versions_non_empty_and_default_included():
    assert SUPPORTED_ERIC_VERSIONS
    assert DEFAULT_ERIC_VERSION in SUPPORTED_ERIC_VERSIONS


def test_version_configs_match_supported_versions():
    for version in SUPPORTED_ERIC_VERSIONS:
        cfg = VERSION_CONFIGS[version]
        assert isinstance(cfg, EricVersionConfig)
        assert cfg.eric_version == version


def test_is_supported_version_and_list_supported_versions():
    all_versions = set(list_supported_versions())
    for version in SUPPORTED_ERIC_VERSIONS:
        assert is_supported_version(version)
        assert version in all_versions


def test_detect_eric_version_from_path():
    """detect_eric_version should parse version from ERIC_HOME path components."""
    # Example with version on the parent directory.
    path = "/opt/ERiC-41.6.2.0/Linux-x86_64"
    detected = detect_eric_version(path)
    assert detected == "41.6.2.0"

    # Example with version as dedicated directory name.
    path2 = "/opt/eric/41.6.2.0/Linux-x86_64"
    detected2 = detect_eric_version(path2)
    assert detected2 == "41.6.2.0"
