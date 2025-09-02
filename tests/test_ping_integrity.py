import pytest

from backend.media import MediaEvent, compute_ping_integrity


def make_event(t, ts):
    return MediaEvent(
        sessionId="s",
        type=t,
        tsDevice=ts,
        playhead=0.0,
        streamType="vod",
        assetType="main",
        params={"s:asset:type": "main"},
    )


def test_ping_integrity_perfect_sequence():
    events = [
        make_event("play", 0),
        make_event("ping", 10000),
        make_event("ping", 20000),
        make_event("sessionEnd", 25000),
    ]
    assert compute_ping_integrity(events) == pytest.approx(100.0, rel=1e-3)


def test_ping_integrity_missing_ping():
    events = [
        make_event("play", 0),
        make_event("ping", 20000),
        make_event("sessionEnd", 25000),
    ]
    assert compute_ping_integrity(events) == pytest.approx(50.0, rel=1e-3)


def test_ping_integrity_short_session_no_expected_pings():
    events = [
        make_event("play", 0),
        make_event("sessionEnd", 5000),
    ]
    assert compute_ping_integrity(events) == 100.0
