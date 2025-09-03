import json
from typing import List, Dict, Any, IO, Optional
from urllib.parse import urlparse, parse_qsl

from .utils import decode_body


def parse_har(file_obj: IO, source_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parse a HTTP Archive (HAR) file into a list of network events.

    The returned events use the same structure as those produced by
    :func:`parse_chlsj` so downstream normalization can operate on either
    format without caring about the original source.  Only a subset of the
    official HAR specification is handled; unknown fields from each entry are
    preserved under the ``raw`` key to aid future debugging.
    """
    data = json.load(file_obj)
    entries = data.get("log", {}).get("entries", [])

    events: List[Dict[str, Any]] = []
    for idx, entry in enumerate(entries):
        request = entry.get("request", {})
        response = entry.get("response", {})
        event: Dict[str, Any] = {
            "url": request.get("url"),
            "method": request.get("method"),
            "status": response.get("status"),
            "startedDateTime": entry.get("startedDateTime"),
            "requestHeaders": {
                h.get("name"): h.get("value") for h in request.get("headers", [])
            },
            "responseHeaders": {
                h.get("name"): h.get("value") for h in response.get("headers", [])
            },
            "postData": request.get("postData"),
            "queryParams": {
                p.get("name"): p.get("value") for p in request.get("queryString", [])
            },
            "bodyJSON": None,
            "raw": entry,
            "source": {"file": source_name, "index": idx},
        }

        # Fallback to parsing query parameters from the URL when the HAR entry
        # does not provide a ``queryString`` array.  Some tools omit the array
        # entirely which would otherwise leave ``queryParams`` empty.
        if not event["queryParams"] and isinstance(event["url"], str):
            parsed = urlparse(event["url"])
            event["queryParams"] = dict(parse_qsl(parsed.query))
        post = event.get("postData") or {}
        text = post.get("text")
        if isinstance(text, str):
            encoding_header = event["requestHeaders"].get("Content-Encoding") or event[
                "requestHeaders"
            ].get("content-encoding")
            try:
                decoded = decode_body(text, encoding_header, post.get("encoding") == "base64")
            except Exception:
                decoded = text
            try:
                event["bodyJSON"] = json.loads(decoded)
            except json.JSONDecodeError:
                pass
        events.append(event)

    return events
