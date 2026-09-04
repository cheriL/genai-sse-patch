import subprocess
import sys

import httpx
import pytest

from ._helpers import acollect_async


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
async def test_async_unpatched_yields_heartbeat_as_chunk():
    code = (
        "import asyncio, httpx\n"
        "from google.genai import _api_client\n"
        "async def run():\n"
        "    raw = b'data: {\"a\": 1}\\n: ping\\n'\n"
        "    transport = httpx.MockTransport(lambda req: httpx.Response(200, content=raw))\n"
        "    async with httpx.AsyncClient(transport=transport) as client:\n"
        "        req = client.build_request('POST', 'http://x/y')\n"
        "        resp = await client.send(req, stream=True)\n"
        "        try:\n"
        "            hr = _api_client.HttpResponse.__new__(_api_client.HttpResponse)\n"
        "            hr.response_stream = resp\n"
        "            chunks = [c async for c in hr._aiter_response_stream()]\n"
        "            assert any(c == ': ping' for c in chunks), chunks\n"
        "        finally:\n"
        "            await resp.aclose()\n"
        "asyncio.run(run())\n"
        "print('ok')\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
