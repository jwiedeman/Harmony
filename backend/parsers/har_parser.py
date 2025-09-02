import json
from typing import List, Dict, Any, IO


def parse_har(file_obj: IO) -> List[Dict[str, Any]]:
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
    for entry in entries:
        request = entry.get("request", {})
        response = entry.get("response", {})
        event: Dict[str, Any] = {
            "url": request.get("url"),
            "method": request.get("method"),
            "status": response.get("status"),
            "startedDateTime": entry.get("startedDateTime"),
            "requestHeaders": {h.get("name"): h.get("value") for h in request.get("headers", [])},
            "responseHeaders": {h.get("name"): h.get("value") for h in response.get("headers", [])},
            "postData": request.get("postData"),
            "queryParams": {p.get("name"): p.get("value") for p in request.get("queryString", [])},
            "bodyJSON": None,
            "raw": entry,
        }
        post = event.get("postData") or {}
        text = post.get("text")
        if isinstance(text, str):
            try:
                event["bodyJSON"] = json.loads(text)
            except json.JSONDecodeError:
                pass
        events.append(event)

    return events
