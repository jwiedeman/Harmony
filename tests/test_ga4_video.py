from backend.ga4 import analyze_video_events


def make_event(name, **params):
    event = {"en": name}
    for key, value in params.items():
        event[f"ep.{key}"] = value
    return event


def test_ga4_video_happy_path():
    events = [
        make_event("video_start", video_title="V", video_duration="100"),
        make_event("video_progress", video_title="V", video_percent="10"),
        make_event("video_progress", video_title="V", video_percent="25"),
        make_event("video_progress", video_title="V", video_percent="50"),
        make_event("video_progress", video_title="V", video_percent="75"),
        make_event(
            "video_complete", video_title="V", video_current_time="95", video_duration="100"
        ),
    ]
    result = analyze_video_events(events)
    assert result["violations"] == []


def test_ga4_video_progress_out_of_order():
    events = [
        make_event("video_start", video_title="V"),
        make_event("video_progress", video_title="V", video_percent="10"),
        make_event("video_progress", video_title="V", video_percent="50"),
    ]
    result = analyze_video_events(events)
    assert any("expected 25" in v for v in result["violations"])


def test_ga4_video_complete_too_early():
    events = [
        make_event("video_start", video_title="V"),
        make_event(
            "video_complete", video_title="V", video_current_time="30", video_duration="100"
        ),
    ]
    result = analyze_video_events(events)
    assert any("95%" in v for v in result["violations"])
