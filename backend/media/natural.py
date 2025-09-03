"""Lightweight sequence signature and anomaly detection helpers.

This module implements a minimal subset of the "natural engine" described in
project docs.  It provides utilities for collapsing a sequence of media event
names into a compact signature string and measuring the distance to reference
signatures.  The implementation is intentionally simple but offers a useful
foundation for future, more sophisticated analysis.
"""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple, Any, Dict

try:  # ``MediaEvent`` is optional to avoid import cycles during type checking
    from .models import MediaEvent  # type: ignore
except Exception:  # pragma: no cover - fallback when models unavailable
    MediaEvent = Any  # type: ignore

# Map known event types to single-character symbols.  Unknown events collapse to
# ``X`` which keeps the signature deterministic while signalling an unrecognised
# verb.
_SYMBOL_MAP = {
    "sessionStart": "S",
    "play": "P",
    "ping": "p",
    "pauseStart": "U",
    "bufferStart": "B",
    "complete": "E",
    "sessionEnd": "E",
    "adStart": "A",
    "adComplete": "a",
    "adBreakStart": "R",
    "adBreakComplete": "r",
}


def _event_type(event: MediaEvent | Dict[str, Any]) -> str | None:
    """Return the event type from ``event``."""

    if hasattr(event, "type"):
        return str(getattr(event, "type"))
    if isinstance(event, dict):
        typ = event.get("type")
        if typ is not None:
            return str(typ)
    return None


def canonical_symbol(event_type: str) -> str:
    """Return canonical single-character symbol for ``event_type``."""

    return _SYMBOL_MAP.get(event_type, "X")


def sequence_signature(events: Iterable[MediaEvent | Dict[str, Any]]) -> str:
    """Collapse ``events`` into a compact signature string.

    Each event contributes a single-character symbol based on its type.  Unknown
    event names are represented by ``X`` to keep signatures stable across
    versions and future extensions.
    """

    symbols = []
    for event in events:
        typ = _event_type(event)
        if typ:
            symbols.append(canonical_symbol(typ))
    return "".join(symbols)


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings."""

    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def sequence_distance(signature: str, templates: Sequence[str]) -> int:
    """Return minimal edit distance from ``signature`` to ``templates``."""

    return min(_levenshtein(signature, t) for t in templates) if templates else len(signature)


def detect_sequence_anomaly(
    events: Iterable[MediaEvent | Dict[str, Any]],
    templates: Sequence[str],
    max_distance: int = 0,
) -> Tuple[bool, int, str]:
    """Detect whether ``events`` deviate from ``templates``.

    Parameters
    ----------
    events:
        Iterable of events (either :class:`MediaEvent` or dictionaries).
    templates:
        Sequence of reference signature strings representing "known good"
        sequences.
    max_distance:
        Maximum allowed edit distance.  Distances greater than this threshold
        are considered anomalous.

    Returns
    -------
    tuple
        ``(is_anomalous, distance, signature)`` where ``signature`` is the
        compact representation of ``events``.
    """

    sig = sequence_signature(events)
    dist = sequence_distance(sig, templates)
    return dist > max_distance, dist, sig


__all__ = [
    "sequence_signature",
    "canonical_symbol",
    "sequence_distance",
    "detect_sequence_anomaly",
]
