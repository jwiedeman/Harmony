import io
import json

from backend.parsers.har_parser import parse_har


def test_parse_har_basic():
    sample = {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2023-01-01T00:00:00Z",
                    "request": {
                        "url": "https://example.com/v1/events",
                        "method": "POST",
                        "headers": [{"name": "Content-Type", "value": "application/json"}],
                        "queryString": [
                            {"name": "s:event:type", "value": "play"},
                            {"name": "s:event:sid", "value": "abc123"},
                            {"name": "l:event:ts", "value": "1712345678901"},
                            {"name": "l:event:playhead", "value": "12.34"},
                            {"name": "s:stream:type", "value": "vod"},
                            {"name": "s:asset:type", "value": "main"}
                        ],
                        "postData": {"text": "{\"foo\": \"bar\"}"},
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }
    events = parse_har(io.StringIO(json.dumps(sample)))
    assert len(events) == 1
    ev = events[0]
    assert ev["url"] == "https://example.com/v1/events"
    assert ev["queryParams"]["s:event:type"] == "play"
    assert ev["bodyJSON"] == {"foo": "bar"}


def test_parse_har_query_from_url():
    sample = {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2023-01-01T00:00:00Z",
                    "request": {
                        "url": "https://example.com/v1/events?alpha=1&beta=two",
                        "method": "GET",
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }
    events = parse_har(io.StringIO(json.dumps(sample)))
    assert events[0]["queryParams"] == {"alpha": "1", "beta": "two"}
