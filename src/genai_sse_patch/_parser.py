from typing import Any, Iterator

from google.genai import _api_client

_HTTPX_RESPONSE_TYPES = _api_client._HTTPX_RESPONSE_TYPES
_HAS_AIOHTTP = _api_client.has_aiohttp
_READ_BUFFER_SIZE = _api_client.READ_BUFFER_SIZE
_loaded_requests = _api_client._common.loaded_requests


class _SseParser:
    def __init__(self) -> None:
        self._chunk = ""
        self._balance = 0
        self._data_buffer: list[str] = []

    def feed(self, line: str) -> list[str]:
        if not line:
            if self._data_buffer:
                out = ["\n".join(self._data_buffer)]
                self._data_buffer = []
                return out
            return []
        if line.startswith(": "):
            return []
        if line.startswith("data: "):
            self._data_buffer.append(line[len("data: "):])
            return []
        for c in line:
            if c == "{":
                self._balance += 1
            elif c == "}":
                self._balance -= 1
        self._chunk += line
        if self._balance == 0:
            out = [self._chunk]
            self._chunk = ""
            return out
        return []

    def flush(self) -> list[str]:
        out: list[str] = []
        if self._chunk:
            out.append(self._chunk)
            self._chunk = ""
        if self._data_buffer:
            out.append("\n".join(self._data_buffer))
            self._data_buffer = []
        return out


def _patched_iter(self) -> Iterator[str]:
    requests_module = _loaded_requests()
    if isinstance(self.response_stream, _HTTPX_RESPONSE_TYPES):
        line_iter = self.response_stream.iter_lines()
    elif (
        requests_module is not None
        and isinstance(self.response_stream, requests_module.Response)
    ):
        line_iter = self.response_stream.iter_lines(decode_unicode=True)
    else:
        raise TypeError(
            "Expected self.response_stream to be an httpx.Response object, "
            f"but got {type(self.response_stream).__name__}."
        )
    parser = _SseParser()
    for line in line_iter:
        yield from parser.feed(line)
    yield from parser.flush()


async def _patched_aiter(self) -> Any:
    if isinstance(self.response_stream, _HTTPX_RESPONSE_TYPES):
        try:
            parser = _SseParser()
            async for line in self.response_stream.aiter_lines():
                for piece in parser.feed(line):
                    yield piece
            for piece in parser.flush():
                yield piece
        finally:
            await self.response_stream.aclose()
        return
    if _HAS_AIOHTTP and isinstance(
        self.response_stream, _api_client.aiohttp.ClientResponse
    ):
        try:
            parser = _SseParser()
            while True:
                try:
                    line_bytes = await self.response_stream.content.readline(
                        max_line_length=_READ_BUFFER_SIZE
                    )
                except TypeError:
                    line_bytes = await self.response_stream.content.readline()
                if not line_bytes:
                    break
                for piece in parser.feed(line_bytes.decode("utf-8").rstrip()):
                    yield piece
            for piece in parser.flush():
                yield piece
        finally:
            self.response_stream.release()
        return
    raise TypeError(
        "Expected self.response_stream to be an httpx.Response or"
        " aiohttp.ClientResponse object, but got"
        f" {type(self.response_stream).__name__}."
    )
