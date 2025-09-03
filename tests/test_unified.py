from backend.unified import to_unified_requests, UnifiedRequest


def make_event(url: str) -> dict:
    return {
        "url": url,
        "method": "GET",
        "status": 200,
        "startedDateTime": "2024-01-01T00:00:00Z",
        "requestHeaders": {},
        "responseHeaders": {},
        "queryParams": {},
        "bodyJSON": {},
        "source": {"file": "test.har", "index": 0},
    }


def test_unified_request_fingerprint_and_parts():
    events = [make_event("https://example.adobedc.net/ee/v1/collect?x=1")]
    unified = to_unified_requests(events)
    assert len(unified) == 1
    req = unified[0]
    assert isinstance(req, UnifiedRequest)
    assert req.host == "example.adobedc.net"
    assert req.path == "/ee/v1/collect"
    assert req.vendor == "adobe"
    assert req.transport == "edge"
    assert req.profile == "web"
    assert req.platform is None
    assert req.source["file"] == "test.har"


def test_unified_request_unknown_vendor():
    events = [make_event("https://example.com/path")]
    req = to_unified_requests(events)[0]
    assert req.vendor is None
    assert req.transport is None
    assert req.profile is None
    assert req.platform is None


def test_unified_request_with_platform():
    event = make_event("https://example.adobedc.net/ee/v1/collect?x=1")
    event["requestHeaders"] = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5)"
    }
    req = to_unified_requests([event])[0]
    assert req.platform == "android"
