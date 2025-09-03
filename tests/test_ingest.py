import io
import json
from backend.ingest import ingest_file


def _sample_entry():
    return {
        "log": {
            "entries": [
                {
                    "startedDateTime": "2023-01-01T00:00:00Z",
                    "request": {
                        "url": "https://example.com/v1/events",
                        "method": "GET",
                        "headers": [],
                        "queryString": [],
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }


def test_ingest_file_har():
    sample = _sample_entry()
    reqs = ingest_file(io.StringIO(json.dumps(sample)), "file.har")
    assert len(reqs) == 1
    req = reqs[0]
    assert req.url == "https://example.com/v1/events"
    assert req.source == {"file": "file.har", "index": 0}


def test_ingest_file_chlsj():
    sample = _sample_entry()
    reqs = ingest_file(io.StringIO(json.dumps(sample)), "file.chlsj")
    assert len(reqs) == 1
    assert reqs[0].url == "https://example.com/v1/events"
    assert reqs[0].source["file"] == "file.chlsj"
