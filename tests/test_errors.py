"""FFI error handling tests for ERiC wrapper."""

from eric_py.errors import EricError, check_eric_result
from eric_py.types import EricErrorCode


def test_check_eric_result_ok_does_not_raise():
    check_eric_result(EricErrorCode.ERIC_OK)


def test_check_eric_result_raises_on_error():
    code = EricErrorCode.ERIC_GLOBAL_UNKNOWN
    try:
        check_eric_result(code, message="boom")
    except EricError as exc:
        assert exc.code == code
        assert "boom" in str(exc)
    else:
        assert False, "EricError was not raised"
