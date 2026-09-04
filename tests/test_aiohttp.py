from unittest.mock import AsyncMock, Mock

import pytest


@pytest.mark.asyncio
async def test_aiohttp_sse_comments_are_dropped():
    aiohttp = pytest.importorskip("aiohttp")

    from ._helpers import acollect_async

    raw = (
        b'data: {"a": 1}\n'
        b": ping\n"
        b'data: {"b": 2}\n'
        b"\n"
    )

    lines = raw.splitlines(keepends=True)

    async def readline(*args, **kwargs):
        return lines.pop(0) if lines else b""

    fake_resp = Mock(spec=aiohttp.ClientResponse)
    fake_resp.content.readline = readline
    fake_resp.release = Mock()

    assert await acollect_async(fake_resp) == [
        '{"a": 1}\n{"b": 2}'
    ]
