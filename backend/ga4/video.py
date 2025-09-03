from __future__ import annotations

"""Simple GA4 video event sanity checks.

The implementation targets the small set of video events emitted by GA4's
enhanced measurement on the web: ``video_start``, ``video_progress`` and
``video_complete``.  The helper focuses on a few high value validations:

* progress percent events must appear in the expected order ``10 → 25 → 50 → 75``
* ``video_complete`` should only fire after roughly 95% of the video was
  watched
* the video title should remain stable throughout the session

The analyser is intentionally lightweight and speculatively normalises GA4
network events to make unit testing straightforward.  The events iterable is
expected to yield dictionaries with an ``en`` key for the event name and GA4
``event parameter`` fields using either ``ep.<name>`` or plain ``<name>`` keys.
"""

from typing import Iterable, Dict, Any, List, Optional

_EXPECTED_PROGRESS = [10, 25, 50, 75]


def _extract_number(value: Any) -> Optional[float]:
    """Best-effort conversion to ``float`` returning ``None`` on failure."""

    try:
        return float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None


def analyze_video_events(events: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Analyse GA4 video ``events`` returning a list of violations.

    Parameters
    ----------
    events:
        Iterable of dictionaries representing network events.  Only the
        ``en`` field and a handful of ``ep.`` parameters are consulted.

    Returns
    -------
    dict
        Mapping with a single ``violations`` key containing human readable
        messages.
    """

    violations: List[str] = []
    title: Optional[str] = None
    next_expected_index = 0
    complete_percent: Optional[float] = None

    for event in events:
        name = str(event.get("en") or event.get("event_name") or "")
        # Title consistency
        event_title = event.get("ep.video_title") or event.get("video_title")
        if event_title:
            if title is None:
                title = str(event_title)
            elif title != str(event_title):
                violations.append("video_title changed during session")

        if name == "video_progress":
            percent = (
                event.get("ep.video_percent")
                or event.get("epn.percent")
                or event.get("video_percent")
            )
            percent_val = _extract_number(percent)
            if percent_val is None:
                violations.append("video_progress missing percent")
                continue
            expected = (
                _EXPECTED_PROGRESS[next_expected_index]
                if next_expected_index < len(_EXPECTED_PROGRESS)
                else None
            )
            if expected is None:
                violations.append(f"unexpected video_progress {percent_val}")
            elif percent_val != expected:
                violations.append(
                    f"unexpected video progress {percent_val}; expected {expected}"
                )
            else:
                next_expected_index += 1

        elif name == "video_complete":
            percent = (
                event.get("ep.video_percent")
                or event.get("video_percent")
            )
            percent_val = _extract_number(percent)
            if percent_val is None:
                current = _extract_number(
                    event.get("ep.video_current_time")
                    or event.get("video_current_time")
                )
                duration = _extract_number(
                    event.get("ep.video_duration")
                    or event.get("video_duration")
                )
                if current is not None and duration not in (None, 0):
                    percent_val = current / duration * 100.0
            complete_percent = percent_val

    if complete_percent is not None and complete_percent < 95:
        violations.append("video_complete before 95% watched")

    return {"violations": violations}


__all__ = ["analyze_video_events"]
