from backend.fingerprint import fingerprint_event


def test_fingerprint_adobe_edge():
    event = {"url": "https://example.adobedc.net/ee/v1/interact"}
    fp = fingerprint_event(event)
    assert fp["vendor"] == "adobe"
    assert fp["transport"] == "edge"
    assert fp["profile"] == "web"


def test_fingerprint_adobe_heartbeat():
    event = {"url": "https://metrics.hb-api.omtrdc.net/x"}
    fp = fingerprint_event(event)
    assert fp["vendor"] == "adobe"
    assert fp["transport"] == "heartbeat"
    assert fp["profile"] == "legacy"


def test_fingerprint_aa_classic():
    event = {"url": "https://example.sc.omtrdc.net/b/ss/rsid/0"}
    fp = fingerprint_event(event)
    assert fp["vendor"] == "adobe"
    assert fp["transport"] == "aa_classic"
    assert fp["profile"] == "web"


def test_fingerprint_ga4():
    event = {"url": "https://www.google-analytics.com/g/collect?v=2"}
    fp = fingerprint_event(event)
    assert fp["vendor"] == "ga4"
    assert fp["transport"] == "measurement"
    assert fp["profile"] == "web"


def test_fingerprint_unknown():
    event = {"url": "https://example.com/"}
    fp = fingerprint_event(event)
    assert fp["vendor"] is None
    assert fp["transport"] is None
    assert fp["profile"] is None
