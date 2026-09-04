"""Drop SSE comment lines in google-genai stream iterators."""
import os

from ._patch import apply

__all__ = ["apply"]
__version__ = "0.1.0"

if os.getenv("GOOGLE_GENAI_SSE_PATCH", "").strip().lower() in {"1", "true", "yes", "on"}:
    apply()
