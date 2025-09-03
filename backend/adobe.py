from __future__ import annotations

"""Adobe-specific helpers."""

from typing import Dict, Any, List
from urllib.parse import urlparse


def extract_rsid(event: Dict[str, Any]) -> List[str]:
    """Return report suite IDs present on an analytics ``event``.

    The helper looks for RSIDs in the classic `/b/ss/<rsid>/` path as well as
    in the `rsid` or `rsid_list` query parameters.  Duplicate values are
    removed and the resulting list is sorted for stable summaries.
    """

    rsids: List[str] = []
    url = str(event.get("url") or "")
    parsed = urlparse(url)
    path = parsed.path.lower()
    if "/b/ss/" in path:
        segment = path.split("/b/ss/", 1)[1]
        parts = segment.split("/", 1)[0]
        rsids.extend([r.strip() for r in parts.split(",") if r.strip()])

    params = event.get("queryParams") or {}
    rsid_param = params.get("rsid")
    if isinstance(rsid_param, str) and rsid_param:
        rsids.append(rsid_param.strip())
    rsid_list = params.get("rsid_list")
    if isinstance(rsid_list, str) and rsid_list:
        rsids.extend([r.strip() for r in rsid_list.split(",") if r.strip()])

    # Return unique, sorted list
    return sorted(set(rsids))


__all__ = ["extract_rsid"]
