from google.genai import _api_client

from ._parser import _patched_aiter, _patched_iter

_INSTALLED = False
_ORIGINAL_SYNC = None
_ORIGINAL_ASYNC = None


def is_installed() -> bool:
    return _INSTALLED


def install() -> None:
    global _INSTALLED, _ORIGINAL_SYNC, _ORIGINAL_ASYNC
    if _INSTALLED:
        return
    cls = _api_client.HttpResponse
    _ORIGINAL_SYNC = cls._iter_response_stream
    _ORIGINAL_ASYNC = cls._aiter_response_stream
    cls._iter_response_stream = _patched_iter
    cls._aiter_response_stream = _patched_aiter
    _INSTALLED = True


def uninstall() -> None:
    global _INSTALLED, _ORIGINAL_SYNC, _ORIGINAL_ASYNC
    if not _INSTALLED:
        return
    cls = _api_client.HttpResponse
    cls._iter_response_stream = _ORIGINAL_SYNC
    cls._aiter_response_stream = _ORIGINAL_ASYNC
    _ORIGINAL_SYNC = _ORIGINAL_ASYNC = None
    _INSTALLED = False
