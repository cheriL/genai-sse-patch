# genai-sse-patch

Drop SSE comment lines in [google-genai](https://github.com/googleapis/python-genai) stream iterators.

`google-genai`'s `HttpResponse._iter_response_stream` / `_aiter_response_stream` only strip `data: ` lines. SSE comment lines (e.g. `: heartbeat`, `: ping`) fall through to the brace-balance fallback and get yielded as JSON chunks, crashing `_load_json_from_response` with:

```
google.genai.errors.UnknownApiResponseError: Failed to parse response as JSON. Raw response: : heartbeat
```

This package replaces those iterators so comment lines are dropped per the SSE spec (HTML5 §6).

## Install

```bash
pip install genai-sse-patch
```

## Usage

Opt in via env var (no code change):

```bash
GOOGLE_GENAI_SSE_PATCH=1 python my_app.py
```

Or call explicitly:

```python
import genai_sse_patch
genai_sse_patch.install()
```

`install()` is idempotent. `uninstall()` restores the SDK originals.

## License

Apache-2.0.
