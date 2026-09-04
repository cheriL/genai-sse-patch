import httpx
import pytest

from ._helpers import acollect_async, make_response


@pytest.mark.asyncio
async def test_async_sse_comments_are_dropped():
    raw = (
        b'data: {"a": 1}\n'
        b": ping\n"
        b'data: {"b": 2}\n'
        b"\n"
        b': keep-alive\n'
    )
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=raw))
    async with httpx.AsyncClient(transport=transport) as client:
        req = client.build_request("POST", "http://x/y")
        resp = await client.send(req, stream=True)
        try:
            assert await acollect_async(resp) == ['{"a": 1}\n{"b": 2}']
        finally:
            await resp.aclose()


@pytest.mark.asyncio
async def test_async_uninstall_restores_original_behaviour():
    from genai_sse_patch import install, uninstall

    install()
    uninstall()
    raw = b'data: {"a": 1}\n: ping\n'
    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=raw))
    async with httpx.AsyncClient(transport=transport) as client:
        req = client.build_request("POST", "http://x/y")
        resp = await client.send(req, stream=True)
        try:
            hr = make_response(resp)
            chunks = []
            async for c in hr._aiter_response_stream():
                chunks.append(c)
            assert any(c == ": ping" for c in chunks)
        finally:
            await resp.aclose()
