import pytest

from genai_sse_patch import install, uninstall
from genai_sse_patch import _patch

from ._helpers import collect_sync, make_httpx_response


def test_install_is_idempotent_and_uninstall_restores():
    install()
    assert _patch.is_installed()
    install()
    assert _patch.is_installed()
    uninstall()
    assert not _patch.is_installed()
    uninstall()
    assert not _patch.is_installed()


def test_sse_comments_are_dropped():
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


def test_uninstall_restores_original_behaviour():
    install()
    uninstall()
    raw = b'data: {"a": 1}\n: ping\n'
    chunks = list(make_httpx_response(raw)._iter_response_stream())
    assert any(c == ": ping" for c in chunks)


def test_balance_fallback_still_yields_brace_json():
    raw = b'{"foo": 1}\n{"bar": 2}\n'
    assert collect_sync(make_httpx_response(raw).response_stream) == [
        '{"foo": 1}',
        '{"bar": 2}',
    ]
