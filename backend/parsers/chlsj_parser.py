import json
from typing import List, Dict, Any, IO
from urllib.parse import urlparse, parse_qsl


def parse_chlsj(file_obj: IO) -> List[Dict[str, Any]]:
    """Parse a Charles .chlsj session file into a list of network events.

    The returned structure roughly matches the NetworkEvent schema used
    elsewhere in Harmony.  Only a subset of fields are extracted; unknown
    fields are preserved under the ``raw`` key so future processing can
    access them if needed.
    """
    data = json.load(file_obj)
    # Charles exports are similar to HAR.  We try a couple of common
    # locations where the entries array might live.
    entries = (
        data.get("log", {}).get("entries")
        or data.get("entries")
        or []
    )

    events: List[Dict[str, Any]] = []
    for entry in entries:
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
        }

        # Some Charles exports omit the ``queryString`` array when the request
        # URL already contains encoded parameters.  In those cases fall back to
        # parsing the query portion of the URL so downstream normalization sees
        # a consistent ``queryParams`` mapping.
        if not event["queryParams"] and isinstance(event["url"], str):
            parsed = urlparse(event["url"])
            event["queryParams"] = dict(parse_qsl(parsed.query))
        post = event.get("postData") or {}
        text = post.get("text")
        if isinstance(text, str):
            try:
                event["bodyJSON"] = json.loads(text)
            except json.JSONDecodeError:
                # leave bodyJSON as None if the payload isn't valid JSON
                pass
        events.append(event)

    return events
