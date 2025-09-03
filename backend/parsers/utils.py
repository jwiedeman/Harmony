import base64
import gzip
import zlib
from typing import Optional

try:
    import brotli  # type: ignore
except Exception:  # pragma: no cover - brotli is optional
    brotli = None

def decode_body(text: str, content_encoding: Optional[str], is_base64: bool) -> str:
    """Decode an HTTP message body.

    Parameters
    ----------
    text:
        The body payload. May be plain text or base64 encoded.
    content_encoding:
        Value of the ``Content-Encoding`` header. Supported values are
        ``gzip``, ``deflate`` and ``br``.
    is_base64:
        ``True`` if ``text`` is base64 encoded.

    Returns
    -------
    str
        The decoded body as a UTF-8 string. Errors are replaced during
        decoding to avoid hard failures when the payload is not valid UTF-8.
    """
    data = base64.b64decode(text) if is_base64 else text.encode("utf-8")
    encoding = (content_encoding or "").lower()
    if encoding == "gzip":
        data = gzip.decompress(data)
    elif encoding == "deflate":
        data = zlib.decompress(data)
    elif encoding in ("br", "brotli"):
        if brotli is None:
            raise RuntimeError("brotli package is required for brotli decoding")
        data = brotli.decompress(data)
    return data.decode("utf-8", errors="replace")
