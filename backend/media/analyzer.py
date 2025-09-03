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

from collections import defaultdict
from typing import Iterable, Dict, Any

from .models import MediaEvent
from .normalize import network_events_to_media_events
from .state_machine import validate_event_order
from .timing import validate_ping_cadence, compute_ping_integrity
from .metrics import compute_basic_metrics
from .params import validate_param_rules


def analyze_session(
    events: Iterable[MediaEvent],
    param_rules: Iterable["ParamRule"] | None = None,
) -> Dict[str, Any]:
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
            under ``ordering``, ``timing`` and, when ``param_rules`` are
            supplied, ``params``.
    """

    from ..scenarios.schema import ParamRule  # local import to avoid cycle

    ordered = sorted(events, key=lambda e: e.tsDevice)
    violations = {
        "ordering": validate_event_order(ordered),
        "timing": validate_ping_cadence(ordered),
        "params": [],
    }
    if param_rules:
        # Coerce to ParamRule instances in case plain dictionaries were passed
        rules = [r if isinstance(r, ParamRule) else ParamRule(**r) for r in param_rules]
        violations["params"] = validate_param_rules(ordered, rules)
    metrics = compute_basic_metrics(ordered)
    metrics["ping_integrity"] = compute_ping_integrity(ordered)
    return {"metrics": metrics, "violations": violations}


def analyze_network_log(
    events: Iterable[Dict[str, Any]],
    param_rules: Iterable["ParamRule"] | None = None,
) -> Dict[str, Any]:
    """Analyze a raw network log represented as dictionaries.

    This helper first normalizes the network entries using
    :func:`network_events_to_media_events` before delegating to
    :func:`analyze_session`.
    """

    media_events = network_events_to_media_events(events)
    return analyze_session(media_events, param_rules=param_rules)


def analyze_sessions(
    events: Iterable[MediaEvent],
    param_rules: Iterable["ParamRule"] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Analyze multiple sessions in one pass.

    Parameters
    ----------
    events:
        Iterable of :class:`MediaEvent` objects from potentially many
        sessions.  The helper groups events by their ``sessionId`` and runs
        :func:`analyze_session` for each group.

    param_rules:
        Optional parameter validation rules applied to every session.

    Returns
    -------
    dict
        Mapping of ``sessionId`` to the same analysis dictionary returned by
        :func:`analyze_session`.
    """

    from ..scenarios.schema import ParamRule  # local import to avoid cycle

    grouped: Dict[str, list[MediaEvent]] = defaultdict(list)
    for event in events:
        grouped[event.sessionId].append(event)

    result: Dict[str, Dict[str, Any]] = {}
    for session_id, sess_events in grouped.items():
        result[session_id] = analyze_session(sess_events, param_rules=param_rules)
    return result


def analyze_network_log_sessions(
    events: Iterable[Dict[str, Any]],
    param_rules: Iterable["ParamRule"] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Analyze a network log containing events from multiple sessions.

    The function normalizes ``events`` using
    :func:`network_events_to_media_events` and delegates to
    :func:`analyze_sessions`.
    """

    media_events = network_events_to_media_events(events)
    return analyze_sessions(media_events, param_rules=param_rules)


__all__ = [
    "analyze_session",
    "analyze_network_log",
    "analyze_sessions",
    "analyze_network_log_sessions",
]
