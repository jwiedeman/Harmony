import pytest

from backend.media import MediaEvent, validate_event_order


def make_event(event_type, ts, **kwargs):
    params = kwargs.pop("params", {})
    return MediaEvent(
        sessionId=kwargs.get("sessionId", "s1"),
        type=event_type,
        tsDevice=ts,
        playhead=kwargs.get("playhead", 0.0),
        streamType=kwargs.get("streamType"),
        assetType=kwargs.get("assetType"),
        params=params,
    )


def test_valid_ad_sequence():
    events = [
        make_event("sessionStart", 0),
        make_event("play", 1000),
        make_event("adBreakStart", 2000),
        make_event("adStart", 2500, assetType="ad"),
        make_event("adComplete", 3500, assetType="ad"),
        make_event("adBreakComplete", 3600),
        make_event("sessionComplete", 4000),
    ]
    assert validate_event_order(events) == []


def test_ad_start_without_break():
    events = [
        make_event("sessionStart", 0),
        make_event("play", 1000),
        make_event("adStart", 2000, assetType="ad"),
    ]
    violations = validate_event_order(events)
    assert any("adStart without" in v for v in violations)


def test_ad_break_complete_without_ad():
    events = [
        make_event("sessionStart", 0),
        make_event("play", 1000),
        make_event("adBreakStart", 2000),
        make_event("adBreakComplete", 2500),
    ]
    violations = validate_event_order(events)
    assert any("adBreakComplete without adStart" in v for v in violations)


def test_play_while_already_playing():
    events = [
        make_event("sessionStart", 0),
        make_event("play", 1000),
        make_event("play", 2000),
    ]
    violations = validate_event_order(events)
    assert any("play while already playing" in v for v in violations)
