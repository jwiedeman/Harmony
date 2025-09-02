from backend.media import MediaEvent, validate_ping_cadence


def test_ping_cadence_valid_main_and_ad():
    events = [
        MediaEvent(sessionId="1", type="play", tsDevice=0, playhead=0.0, assetType="main"),
        MediaEvent(sessionId="1", type="ping", tsDevice=10000, playhead=10.0, assetType="main"),
        MediaEvent(sessionId="1", type="ping", tsDevice=20000, playhead=20.0, assetType="main"),
        MediaEvent(sessionId="1", type="adStart", tsDevice=30000, playhead=30.0, assetType="ad"),
        MediaEvent(sessionId="1", type="ping", tsDevice=31000, playhead=31.0, assetType="ad"),
        MediaEvent(sessionId="1", type="ping", tsDevice=32000, playhead=32.0, assetType="ad"),
    ]
    assert validate_ping_cadence(events) == []


def test_ping_cadence_missing_main_ping():
    events = [
        MediaEvent(sessionId="1", type="play", tsDevice=0, playhead=0.0, assetType="main"),
        MediaEvent(sessionId="1", type="ping", tsDevice=15000, playhead=15.0, assetType="main"),
    ]
    violations = validate_ping_cadence(events)
    assert violations
    assert any("missing ping" in v for v in violations)


def test_ping_cadence_early_main_ping():
    events = [
        MediaEvent(sessionId="1", type="play", tsDevice=0, playhead=0.0, assetType="main"),
        MediaEvent(sessionId="1", type="ping", tsDevice=1000, playhead=1.0, assetType="main"),
    ]
    violations = validate_ping_cadence(events)
    assert violations
    assert any("early ping" in v for v in violations)
