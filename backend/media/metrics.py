"""Utility functions for computing playback metrics.

This module provides a very small subset of the functionality described in
the full *Harmony Heartbeat+* specification.  Given a chronologically ordered
sequence of :class:`MediaEvent` objects it derives basic duration metrics such
as the amount of time spent watching main content, advertisements, pauses and
buffering.  Durations are calculated using the device timestamp associated with
each event which is reported in milliseconds.

The implementation is intentionally lightweight so that unit tests can exercise
metric calculations without requiring the complete state machine or scenario
DSL that the production system will eventually include.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from .models import MediaEvent


@dataclass
class Metrics:
    """Container for accumulated playback durations in seconds."""

    content: float = 0.0
    ad: float = 0.0
    pause: float = 0.0
    buffer: float = 0.0

    @property
    def total(self) -> float:
        return self.content + self.ad + self.pause + self.buffer


def _state_from_event(event: MediaEvent, current: str | None) -> str | None:
    """Return the playback state implied by ``event``.

    The function only understands a subset of event types.  Any unknown event
    leaves the state unchanged.  ``None`` is used when no playback is active.
    """

    t = event.type
    asset = event.assetType or event.params.get("s:asset:type")

    if t in {"play", "ping"}:
        # Ping events maintain the current state but still advertise the asset
        # type so treat them the same as a play for the purposes of state
        # tracking.
        return "ad" if asset == "ad" else "main"
    if t == "adStart":
        return "ad"
    if t == "adComplete":
        return "main"
    if t == "pauseStart":
        return "pause"
    if t == "bufferStart":
        return "buffer"
    if t in {"sessionEnd", "sessionComplete"}:
        return None
    # Resume from pause or buffer is signalled by a play which is handled
    # above; otherwise leave the state unchanged.
    return current


def compute_basic_metrics(events: Iterable[MediaEvent]) -> Dict[str, float]:
    """Compute simple playback metrics from ``events``.

    Parameters
    ----------
    events:
        An iterable of :class:`MediaEvent` objects sorted by ``tsDevice``.

    Returns
    -------
    dict
        Mapping with keys ``content``, ``ad``, ``pause``, ``buffer`` and
        ``total`` representing the number of seconds spent in each state.

    Notes
    -----
    The function does **not** attempt to validate ordering rules or ping
    cadence.  It merely integrates time deltas between successive events based
    on their implied playback state.
    """

    iterator = iter(sorted(events, key=lambda e: e.tsDevice))
    try:
        first = next(iterator)
    except StopIteration:
        return {"content": 0.0, "ad": 0.0, "pause": 0.0, "buffer": 0.0, "total": 0.0}

    metrics = Metrics()
    state = _state_from_event(first, None)
    last_ts = first.tsDevice

    for event in iterator:
        ts = event.tsDevice
        delta = max(0, ts - last_ts) / 1000.0  # convert to seconds

        if state == "main":
            metrics.content += delta
        elif state == "ad":
            metrics.ad += delta
        elif state == "pause":
            metrics.pause += delta
        elif state == "buffer":
            metrics.buffer += delta

        state = _state_from_event(event, state)
        last_ts = ts

    return {
        "content": metrics.content,
        "ad": metrics.ad,
        "pause": metrics.pause,
        "buffer": metrics.buffer,
        "total": metrics.total,
    }


__all__ = ["compute_basic_metrics"]

