import pytest

from backend.media.natural import sequence_signature, detect_sequence_anomaly


def _events(types):
    return [{"type": t} for t in types]


def test_sequence_signature_basic():
    events = _events(["sessionStart", "play", "ping", "ping", "sessionEnd"])
    assert sequence_signature(events) == "SPppE"


def test_detect_sequence_anomaly():
    events = _events(["sessionStart", "play", "ping", "sessionEnd"])
    anomalous, distance, signature = detect_sequence_anomaly(events, ["SPppE"], max_distance=0)
    assert signature == "SPpE"
    assert distance == 1
    assert anomalous is True
