from __future__ import annotations

"""Simple validator for Adobe Media event ordering.

The implementation only covers a subset of the full Harmony Heartbeat+
state machine.  It focuses on ad break sequencing so that unit tests can
verify basic correctness rules without requiring the complete timing and
ping cadence logic described in the specification.

The validator exposes a single :func:`validate_event_order` function that
accepts a sequence of :class:`MediaEvent` objects and returns a list of
human readable violation messages.  An empty list indicates that the
sequence adhered to the small set of rules currently implemented.
"""

from typing import Iterable, List

from .models import MediaEvent


class _PlaybackState:
    """Internal enumeration of coarse playback states."""

    IDLE = "idle"
    MAIN = "main"
    PAUSED = "paused"
    BUFFERING = "buffering"
    AD = "ad"


def validate_event_order(events: Iterable[MediaEvent]) -> List[str]:
    """Validate ordering of media events.

    Parameters
    ----------
    events:
        Chronologically ordered :class:`MediaEvent` objects belonging to a
        single session.

    Returns
    -------
    list of str
        A list of human readable violation messages.  The list will be
        empty if no problems were detected.
    """

    state = _PlaybackState.IDLE
    ad_break_active = False
    ad_active = False
    ad_started_in_break = False
    violations: List[str] = []

    for event in events:
        t = event.type

        if t == "sessionStart":
            state = _PlaybackState.MAIN
            ad_break_active = False
            ad_active = False
            continue

        if t == "play":
            # Resume from pause or buffer
            state = _PlaybackState.MAIN
            continue

        if t == "pauseStart":
            state = _PlaybackState.PAUSED
            continue

        if t == "bufferStart":
            state = _PlaybackState.BUFFERING
            continue

        if t == "adBreakStart":
            if ad_break_active or ad_active:
                violations.append("adBreakStart while previous ad break active")
            else:
                ad_break_active = True
                ad_started_in_break = False
            continue

        if t == "adStart":
            if not ad_break_active or ad_active:
                violations.append("adStart without preceding adBreakStart")
            else:
                ad_active = True
                ad_started_in_break = True
                state = _PlaybackState.AD
            continue

        if t == "adComplete":
            if not ad_active:
                violations.append("adComplete without preceding adStart")
            else:
                ad_active = False
                state = _PlaybackState.MAIN
            continue

        if t == "adBreakComplete":
            if ad_active:
                violations.append("adBreakComplete before adComplete")
                ad_active = False
            if not ad_break_active:
                violations.append("adBreakComplete without adBreakStart")
            elif not ad_started_in_break:
                # ad_break_active True but no ad ever started
                violations.append("adBreakComplete without adStart")
            ad_break_active = False
            ad_started_in_break = False
            state = _PlaybackState.MAIN
            continue

        if t in {"sessionEnd", "sessionComplete"}:
            if ad_active:
                violations.append("session ended during active ad")
                ad_active = False
            if ad_break_active:
                violations.append("session ended during active ad break")
                ad_break_active = False
            state = _PlaybackState.IDLE
            continue

        # Ignore other event types (e.g., ping)

    if ad_active:
        violations.append("ad not closed with adComplete")
    if ad_break_active:
        violations.append("ad break not closed with adBreakComplete")

    return violations


__all__ = ["validate_event_order"]
