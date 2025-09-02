import pytest

from backend.media import MediaEvent, compute_basic_metrics


def build_event(type_, ts, asset="main"):
    return MediaEvent(
        sessionId="s",
        type=type_,
        tsDevice=ts,
        playhead=0.0,
        streamType="vod",
        assetType=asset,
        params={"s:asset:type": asset},
    )


def test_compute_basic_metrics_simple_flow():
    events = [
        build_event("play", 0, "main"),
        build_event("ping", 10000, "main"),
        build_event("pauseStart", 15000, "main"),
        build_event("play", 20000, "main"),
        build_event("ping", 30000, "main"),
        build_event("adStart", 35000, "ad"),
        build_event("ping", 36000, "ad"),
        build_event("adComplete", 37000, "ad"),
        build_event("play", 37000, "main"),
        build_event("sessionComplete", 40000, "main"),
    ]

    metrics = compute_basic_metrics(events)

    assert metrics["content"] == pytest.approx(33.0, rel=1e-3)
    assert metrics["ad"] == pytest.approx(2.0, rel=1e-3)
    assert metrics["pause"] == pytest.approx(5.0, rel=1e-3)
    assert metrics["buffer"] == 0.0
    assert metrics["total"] == pytest.approx(40.0, rel=1e-3)

