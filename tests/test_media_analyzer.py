import pytest

from backend.media import (
    MediaEvent,
    analyze_session,
    analyze_network_log,
    analyze_sessions,
)


def make_event(t, ts, asset="main"):
    return MediaEvent(
        sessionId="s",
        type=t,
        tsDevice=ts,
        playhead=0.0,
        streamType="vod",
        assetType=asset,
        params={"s:asset:type": asset},
    )


def test_analyze_session_combines_metrics_and_violations():
    events = [
        make_event("play", 0, "main"),
        # missing ping at 10s -> cadence violation
        make_event("ping", 15000, "main"),
        # adStart without adBreakStart -> ordering violation
        make_event("adStart", 20000, "ad"),
        make_event("adComplete", 22000, "ad"),
        make_event("sessionEnd", 25000, "main"),
    ]
    result = analyze_session(events)

    # Metrics reflect time spent in each asset
    assert result["metrics"]["content"] == pytest.approx(23.0, rel=1e-3)
    assert result["metrics"]["ad"] == pytest.approx(2.0, rel=1e-3)
    assert result["metrics"]["pause"] == 0.0
    assert result["metrics"]["buffer"] == 0.0
    assert result["metrics"]["total"] == pytest.approx(25.0, rel=1e-3)
    assert result["metrics"]["ping_integrity"] < 100.0

    # Violations from ordering and timing components are surfaced
    ordering = " ".join(result["violations"]["ordering"])
    timing = " ".join(result["violations"]["timing"])
    assert "adStart without" in ordering
    assert "missing ping" in timing


def test_analyze_network_log_normalizes_events():
    # Minimal network log representing play then ping
    network_log = [
        {
            "bodyJSON": {
                "s:event:type": "play",
                "s:event:sid": "s",
                "l:event:ts": 0,
                "l:event:playhead": 0,
                "s:stream:type": "vod",
                "s:asset:type": "main",
            }
        },
        {
            "bodyJSON": {
                "s:event:type": "ping",
                "s:event:sid": "s",
                "l:event:ts": 10000,
                "l:event:playhead": 10,
                "s:stream:type": "vod",
                "s:asset:type": "main",
            }
        },
    ]
    result = analyze_network_log(network_log)
    assert result["metrics"]["content"] == pytest.approx(10.0, rel=1e-3)
    assert result["violations"]["ordering"] == []
    assert result["violations"]["timing"] == []


def test_analyze_sessions_groups_results_by_session():
    events = [
        # Events interleaved from two sessions
        MediaEvent(
            sessionId="s1",
            type="play",
            tsDevice=0,
            playhead=0.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
        MediaEvent(
            sessionId="s2",
            type="play",
            tsDevice=0,
            playhead=0.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
        MediaEvent(
            sessionId="s1",
            type="ping",
            tsDevice=10000,
            playhead=10.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
        MediaEvent(
            sessionId="s2",
            type="ping",
            tsDevice=5000,
            playhead=5.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
        MediaEvent(
            sessionId="s2",
            type="sessionEnd",
            tsDevice=10000,
            playhead=10.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
        MediaEvent(
            sessionId="s1",
            type="sessionEnd",
            tsDevice=20000,
            playhead=20.0,
            streamType="vod",
            assetType="main",
            params={"s:asset:type": "main"},
        ),
    ]

    result = analyze_sessions(events)
    assert set(result.keys()) == {"s1", "s2"}
    assert result["s1"]["metrics"]["content"] == pytest.approx(20.0, rel=1e-3)
    assert result["s2"]["metrics"]["content"] == pytest.approx(10.0, rel=1e-3)
