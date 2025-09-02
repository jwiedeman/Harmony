from __future__ import annotations

"""High level helpers for validating Adobe media sessions.

This module ties together the individual components provided by the
:mod:`backend.media` package – normalization, ordering rules, ping cadence
checks and basic metric calculations.  It exposes convenience functions that
accept either already-normalized :class:`MediaEvent` objects or raw network
log entries.  The functions return a dictionary containing computed metrics and
any validation violations that were detected.

The implementation is intentionally lightweight; it focuses on the pieces
implemented in the test suite (event ordering, ping cadence and simple
metrics).  Additional rules can be layered on later without changing the
public interface.
"""

from typing import Iterable, Dict, Any

from .models import MediaEvent
from .normalize import network_events_to_media_events
from .state_machine import validate_event_order
from .timing import validate_ping_cadence
from .metrics import compute_basic_metrics


def analyze_session(events: Iterable[MediaEvent]) -> Dict[str, Any]:
    """Analyze a sequence of :class:`MediaEvent` objects.

    Parameters
    ----------
    events:
        Chronologically ordered ``MediaEvent`` instances.  The helper sorts the
        events by ``tsDevice`` to guard against minor ordering mistakes in the
        input.

    Returns
    -------
    dict
        Mapping with two keys:

        ``metrics``
            Basic playback duration metrics as returned by
            :func:`compute_basic_metrics`.
        ``violations``
            Dictionary containing lists of human readable violation messages
            under ``ordering`` and ``timing``.
    """

    ordered = sorted(events, key=lambda e: e.tsDevice)
    violations = {
        "ordering": validate_event_order(ordered),
        "timing": validate_ping_cadence(ordered),
    }
    metrics = compute_basic_metrics(ordered)
    return {"metrics": metrics, "violations": violations}


def analyze_network_log(events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a raw network log represented as dictionaries.

    This helper first normalizes the network entries using
    :func:`network_events_to_media_events` before delegating to
    :func:`analyze_session`.
    """

    media_events = network_events_to_media_events(events)
    return analyze_session(media_events)


__all__ = ["analyze_session", "analyze_network_log"]
