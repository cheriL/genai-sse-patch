"""Drop SSE comment lines in google-genai stream iterators."""
import os

from ._patch import install, uninstall

__all__ = ["install", "uninstall"]
__version__ = "0.1.0"

if os.getenv("GOOGLE_GENAI_SSE_PATCH", "").strip().lower() in {"1", "true", "yes", "on"}:
    install()
