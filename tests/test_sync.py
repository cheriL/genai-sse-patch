import os
import subprocess
import sys


def _run(code: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = None
    if env is not None:
        full_env = {**os.environ, **env}
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=full_env,
    )


def test_env_var_disabled_leaves_sdk_untouched():
    code = (
        "import os\n"
        "assert os.getenv('GOOGLE_GENAI_SSE_PATCH') is None or not os.getenv('GOOGLE_GENAI_SSE_PATCH').strip()\n"
        "import genai_sse_patch\n"
        "from google.genai import _api_client\n"
        "assert _api_client.HttpResponse._iter_response_stream.__module__ != 'genai_sse_patch._parser'\n"
        "print('ok')\n"
    )
    result = _run(code)
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_env_var_enabled_auto_applies():
    code = (
        "from google.genai import _api_client\n"
        "import genai_sse_patch\n"
        "assert _api_client.HttpResponse._iter_response_stream.__module__ == 'genai_sse_patch._parser'\n"
        "assert _api_client.HttpResponse._aiter_response_stream.__module__ == 'genai_sse_patch._parser'\n"
        "print('ok')\n"
    )
    result = _run(code, env={"GOOGLE_GENAI_SSE_PATCH": "1"})
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_sse_comments_are_dropped():
    from ._helpers import collect_sync, make_httpx_response

    raw = (
        b'data: {"a": 1}\n'
        b": ping\n"
        b'data: {"b": 2}\n'
        b"\n"
        b": keep-alive\n"
    )
    assert collect_sync(make_httpx_response(raw).response_stream) == [
        '{"a": 1}\n{"b": 2}'
    ]


def test_multiline_data_frames_are_buffered():
    from ._helpers import collect_sync, make_httpx_response

    raw = (
        b'data: {"x": 1}\n'
        b'data: {"y": 2}\n'
        b"\n"
        b': ping\n'
        b'data: {"z": 3}\n'
        b"\n"
    )
    assert collect_sync(make_httpx_response(raw).response_stream) == [
        '{"x": 1}\n{"y": 2}',
        '{"z": 3}',
    ]


def test_balance_fallback_still_yields_brace_json():
    from ._helpers import collect_sync, make_httpx_response

    raw = b'{"foo": 1}\n{"bar": 2}\n'
    assert collect_sync(make_httpx_response(raw).response_stream) == [
        '{"foo": 1}',
        '{"bar": 2}',
    ]


def test_unpatched_yields_heartbeat_as_chunk():
    code = (
        "import httpx\n"
        "from google.genai import _api_client\n"
        "raw = b'data: {\"a\": 1}\\n: ping\\n'\n"
        "resp = httpx.Response(200, content=raw)\n"
        "hr = _api_client.HttpResponse.__new__(_api_client.HttpResponse)\n"
        "hr.response_stream = resp\n"
        "chunks = list(hr._iter_response_stream())\n"
        "assert any(c == ': ping' for c in chunks), chunks\n"
        "print('ok')\n"
    )
    result = _run(code)
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
