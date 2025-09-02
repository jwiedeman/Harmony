from backend.media import MediaEvent, analyze_session
from backend.scenarios.schema import ParamRule


def make_event(t, ts, params=None):
    params = params or {}
    return MediaEvent(
        sessionId="s",
        type=t,
        tsDevice=ts,
        playhead=0.0,
        streamType="vod",
        assetType="main",
        params=params,
    )


def test_validate_param_rules_flags_missing_params():
    events = [make_event("play", 0, params={"s:asset:type": "main"})]
    rules = [ParamRule(on="play", require=["s:asset:type", "l:event:playhead"])]
    result = analyze_session(events, param_rules=rules)
    violations = result["violations"]["params"]
    assert any("l:event:playhead" in v for v in violations)
    assert not any("s:asset:type" in v for v in violations)
