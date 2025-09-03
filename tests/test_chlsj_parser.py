import io
import json

from backend.parsers.chlsj_parser import parse_chlsj
import base64
import gzip


def test_parse_chlsj_basic():
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
    events = parse_chlsj(io.StringIO(json.dumps(sample)), "sample.chlsj")
    assert len(events) == 1
    ev = events[0]
    assert ev["url"] == "https://example.com/v1/events"
    assert ev["queryParams"]["s:event:type"] == "play"
    assert ev["bodyJSON"] == {"foo": "bar"}
    assert ev["source"] == {"file": "sample.chlsj", "index": 0}


def test_parse_chlsj_query_from_url():
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
    events = parse_chlsj(io.StringIO(json.dumps(sample)), "sample.chlsj")
    assert events[0]["queryParams"] == {"alpha": "1", "beta": "two"}


def test_parse_chlsj_decompress_body():
    body = json.dumps({"foo": "bar"}).encode("utf-8")
    encoded = base64.b64encode(gzip.compress(body)).decode("ascii")
    sample = {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2023-01-01T00:00:00Z",
                    "request": {
                        "url": "https://example.com/v1/events",
                        "method": "POST",
                        "headers": [{"name": "Content-Encoding", "value": "gzip"}],
                        "postData": {"text": encoded, "encoding": "base64"},
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }
    events = parse_chlsj(io.StringIO(json.dumps(sample)), "sample.chlsj")
    assert events[0]["bodyJSON"] == {"foo": "bar"}
