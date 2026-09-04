from google.genai import _api_client

from ._parser import _patched_aiter, _patched_iter


def apply() -> None:
    cls = _api_client.HttpResponse
    cls._iter_response_stream = _patched_iter
    cls._aiter_response_stream = _patched_aiter
