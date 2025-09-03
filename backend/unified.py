from __future__ import annotations

"""Helpers for normalizing parsed network events."""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from .fingerprint import fingerprint_event


class UnifiedRequest(BaseModel):
    """Normalized representation of a single network request.

    The model captures common attributes shared across the various parsers
    and attaches high level analytics metadata inferred by
    :func:`fingerprint_event`.  It forms the foundation for further vendor
    specific normalization steps.
    """

    ts_wall: Optional[str] = Field(None, description="Wall clock timestamp")
    url: Optional[str] = Field(None, description="Full request URL")
    host: Optional[str] = Field(None, description="Request host name")
    path: Optional[str] = Field(None, description="Request path")
    query: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    method: Optional[str] = Field(None, description="HTTP method")
    status: Optional[int] = Field(None, description="HTTP status code")
    requestHeaders: Dict[str, Any] = Field(default_factory=dict, description="Request headers")
    responseHeaders: Dict[str, Any] = Field(default_factory=dict, description="Response headers")
    body: Any = Field(None, description="Parsed body payload")
    vendor: Optional[str] = Field(None, description="Detected analytics vendor")
    transport: Optional[str] = Field(None, description="Detected transport mechanism")
    profile: Optional[str] = Field(None, description="Detected profile/platform")
    platform: Optional[str] = Field(None, description="Detected client platform")
    sdk_version: Optional[str] = Field(
        None, description="Detected client SDK version"
    )
    source: Dict[str, Any] = Field(default_factory=dict, description="Origin of the request")


def to_unified_requests(events: List[Dict[str, Any]]) -> List[UnifiedRequest]:
    """Convert parsed network ``events`` into :class:`UnifiedRequest` objects."""

    unified: List[UnifiedRequest] = []
    for event in events:
        parsed = urlparse(str(event.get("url") or ""))
        meta = fingerprint_event(event)
        unified.append(
            UnifiedRequest(
                ts_wall=event.get("startedDateTime"),
                url=event.get("url"),
                host=parsed.netloc or None,
                path=parsed.path or None,
                query=event.get("queryParams") or {},
                method=event.get("method"),
                status=event.get("status"),
                requestHeaders=event.get("requestHeaders") or {},
                responseHeaders=event.get("responseHeaders") or {},
                body=event.get("bodyJSON"),
                vendor=meta.get("vendor"),
                transport=meta.get("transport"),
                profile=meta.get("profile"),
                platform=meta.get("platform"),
                sdk_version=meta.get("sdk_version"),
                source=event.get("source") or {},
            )
        )
    return unified


__all__ = ["UnifiedRequest", "to_unified_requests"]
