# genai-sse-patch

[![PyPI](https://img.shields.io/pypi/v/genai-sse-patch.svg)](https://pypi.org/project/genai-sse-patch/)
[![Python](https://img.shields.io/pypi/pyversions/genai-sse-patch.svg)](https://pypi.org/project/genai-sse-patch/)
[![License](https://img.shields.io/github/license/cheriL/genai-sse-patch.svg)](https://github.com/cheriL/genai-sse-patch/blob/master/LICENSE)

Drop SSE comment lines in [`google-genai`](https://github.com/googleapis/python-genai) stream iterators.

## Why

`google-genai`'s stream iterators only strip `data:` lines. SSE comment lines (e.g. `: heartbeat`) leak through as JSON and crash parsing — most often hit on long-running requests or calls proxied through third-party gateways that inject keepalive frames:

```
google.genai.errors.UnknownApiResponseError: Failed to parse response as JSON. Raw response: : heartbeat
```

This package monkey-patches the iterators so comment lines are dropped per the SSE spec.

## Install

```bash
pip install genai-sse-patch
```

## Usage

**Via env var** — apply on import, no code change:

```bash
GOOGLE_GENAI_SSE_PATCH=1 python my_app.py
```

**Or programmatically:**

```python
from google import genai
import genai_sse_patch


genai_sse_patch.apply()
client = genai.Client()

for chunk in client.models.generate_content_stream(
    model="gemini-3.6-flash",
    contents="Hello",
):
    print(chunk.text)
```

## License

Apache-2.0.
