from __future__ import annotations

"""Heuristics for inferring vendor and transport details from requests.

The helpers in this module perform lightweight fingerprinting of network
requests to guess which analytics ecosystem produced them.  The goal is to
attach high level metadata to each parsed request so later processing stages
can route them through the appropriate normalization and validation logic.

Only a handful of common Adobe and Google Analytics routes are recognized.  The
logic is intentionally conservative and returns ``None`` for any attribute that
cannot be confidently determined.
"""

from typing import Dict, Optional
from urllib.parse import urlparse


def _detect_platform(event: Dict[str, object]) -> Optional[str]:
    """Best-effort platform inference from request headers.

    The heuristics are intentionally simple and rely primarily on the
    ``User-Agent`` header.  The goal is to provide a coarse indicator of the
    client environment (web, ios, android, tvos, fire_tv, roku) so later
    processing stages can apply profile specific logic.
    """

    headers = event.get("requestHeaders") or {}
    ua = headers.get("User-Agent") or headers.get("user-agent") or ""
    ua = ua.lower()
    if not ua:
        return None

    # Order matters: check more specific platforms before generic matches.
    if "roku" in ua:
        return "roku"
    if "firetv" in ua or "aft" in ua:
        return "fire_tv"
    if "tvos" in ua or "appletv" in ua or "apple tv" in ua:
        return "tvos"
    if "iphone" in ua or "ipad" in ua or "ipod" in ua:
        return "ios"
    if "android" in ua:
        return "android"
    if "windows" in ua or "macintosh" in ua or "linux" in ua or "mozilla" in ua:
        return "web"
    return None


def fingerprint_event(event: Dict[str, object]) -> Dict[str, Optional[str]]:
    """Return analytics metadata for a single network ``event``.

    Parameters
    ----------
    event:
        Network event dictionary produced by :mod:`backend.parsers`.  Only the
        ``url`` field is required; other fields are ignored.

    Returns
    -------
    dict
        Mapping with ``vendor``, ``transport`` and ``profile`` keys.  Values may
        be ``None`` when the request could not be classified.
    """

    url = str(event.get("url") or "")
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    vendor: Optional[str] = None
    transport: Optional[str] = None
    profile: Optional[str] = None
    platform: Optional[str] = _detect_platform(event)

    # --- Adobe Analytics and Media ---
    if host.endswith("hb-api.omtrdc.net") or host.endswith("hb.omtrdc.net"):
        vendor = "adobe"
        transport = "heartbeat"
        profile = "legacy"
    elif host.endswith("adobedc.net") and "/ee/v1/" in path:
        vendor = "adobe"
        transport = "edge"
        profile = "web"
    elif "/b/ss/" in path:
        vendor = "adobe"
        transport = "aa_classic"
        profile = "web"

    # --- Google Analytics 4 ---
    elif "google-analytics.com" in host or "googletagmanager.com" in host:
        vendor = "ga4"
        transport = "measurement"
        profile = "web"

    return {
        "vendor": vendor,
        "transport": transport,
        "profile": profile,
        "platform": platform,
    }


__all__ = ["fingerprint_event"]
