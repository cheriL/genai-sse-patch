from google.genai import _api_client


def make_response(stream) -> _api_client.HttpResponse:
    hr = _api_client.HttpResponse.__new__(_api_client.HttpResponse)
    hr.response_stream = stream
    return hr


def make_httpx_response(raw: bytes) -> _api_client.HttpResponse:
    import httpx

    return make_response(httpx.Response(200, content=raw))


def collect_sync(stream) -> list[str]:
    import genai_sse_patch

    genai_sse_patch.install()
    return list(make_response(stream)._iter_response_stream())


async def acollect_async(stream) -> list[str]:
    import genai_sse_patch

    genai_sse_patch.install()
    out: list[str] = []
    async for piece in make_response(stream)._aiter_response_stream():
        out.append(piece)
    return out
