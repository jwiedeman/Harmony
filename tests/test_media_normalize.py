import io
import json

from backend.parsers.chlsj_parser import parse_chlsj
from backend.media import network_events_to_media_events


def build_sample_event():
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
                        "postData": {"text": "{}"},
                    },
                    "response": {"status": 200, "headers": []},
                }
            ]
        }
    }
    return sample


def test_network_events_to_media_events():
    events = parse_chlsj(io.StringIO(json.dumps(build_sample_event())))
    media_events = network_events_to_media_events(events)
    assert len(media_events) == 1
    me = media_events[0]
    assert me.sessionId == "abc123"
    assert me.type == "play"
    assert me.tsDevice == 1712345678901
    assert me.playhead == 12.34
    assert me.streamType == "vod"
    assert me.assetType == "main"


def test_network_events_to_media_events_camel_case_fields():
    """Events using camelCase field names are normalized."""
    log = [
        {
            "bodyJSON": {
                "events": [
                    {
                        "eventType": "play",
                        "sessionId": "xyz",
                        "ts": 1000,
                        "playhead": 5.0,
                        "streamType": "vod",
                        "assetType": "main",
                    }
                ]
            },
            "queryParams": {},
        }
    ]
    media_events = network_events_to_media_events(log)
    assert len(media_events) == 1
    me = media_events[0]
    assert me.sessionId == "xyz"
    assert me.type == "play"
    assert me.tsDevice == 1000
    assert me.playhead == 5.0
    assert me.streamType == "vod"
    assert me.assetType == "main"


def test_network_events_to_media_events_form_params():
    """Parameters encoded in POST bodies are recognized."""
    log = [
        {
            "queryParams": {},
            "bodyJSON": None,
            "postData": {
                "params": [
                    {"name": "s:event:type", "value": "play"},
                    {"name": "s:event:sid", "value": "sid123"},
                    {"name": "l:event:ts", "value": "1000"},
                    {"name": "l:event:playhead", "value": "5"},
                    {"name": "s:stream:type", "value": "vod"},
                    {"name": "s:asset:type", "value": "main"},
                ]
            },
        }
    ]
    media_events = network_events_to_media_events(log)
    assert len(media_events) == 1
    me = media_events[0]
    assert me.sessionId == "sid123"
    assert me.type == "play"
    assert me.tsDevice == 1000
    assert me.playhead == 5
    assert me.streamType == "vod"
    assert me.assetType == "main"


def test_session_id_extracted_from_location_header():
    """SessionStart events without a session id in params use response headers."""
    log = [
        {
            "bodyJSON": {
                "events": [
                    {"eventType": "sessionStart", "params": {"l:event:ts": "1000"}}
                ]
            },
            "queryParams": {},
            "responseHeaders": {
                "Location": "https://example.com/v1/sessions/abc123"
            },
        }
    ]
    media_events = network_events_to_media_events(log)
    assert len(media_events) == 1
    me = media_events[0]
    assert me.sessionId == "abc123"
    assert me.type == "sessionStart"
