import io
import json

from backend.parsers import parse_network_file


def _sample_entry():
    return {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2023-01-01T00:00:00Z",
                    "request": {
                        "url": "https://example.com/v1/events",
                        "method": "POST",
                        "headers": [],
                        "queryString": [],
                        "postData": {"text": "{}"},
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }


def test_parse_network_file_har():
    sample = _sample_entry()
    events = parse_network_file(io.StringIO(json.dumps(sample)), "file.har")
    assert len(events) == 1
    assert events[0]["url"] == "https://example.com/v1/events"


def test_parse_network_file_chlsj():
    sample = _sample_entry()
    events = parse_network_file(io.StringIO(json.dumps(sample)), "file.chlsj")
    assert len(events) == 1
    assert events[0]["url"] == "https://example.com/v1/events"
