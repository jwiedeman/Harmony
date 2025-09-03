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


def test_parse_network_file_chls_no_charles(tmp_path):
    path = tmp_path / "file.chls"
    path.write_bytes(b"not-a-real-chls")
    with open(path, "rb") as f:
        try:
            parse_network_file(f, str(path))
        except RuntimeError as e:
            assert "Charles CLI" in str(e)
        else:
            raise AssertionError("RuntimeError expected when Charles CLI missing")


def test_sniff_har_without_extension():
    sample = _sample_entry()
    events = parse_network_file(io.StringIO(json.dumps(sample)), "noext")
    assert len(events) == 1
    assert events[0]["url"] == "https://example.com/v1/events"


def test_sniff_binary_defaults_to_chls(tmp_path):
    path = tmp_path / "capture"  # no extension
    path.write_bytes(b"\x00\x01binary")
    with open(path, "rb") as f:
        try:
            parse_network_file(f, str(path))
        except RuntimeError as e:
            assert "Charles CLI" in str(e)
        else:
            raise AssertionError("RuntimeError expected when Charles CLI missing")
