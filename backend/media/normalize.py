from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .models import MediaEvent


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def network_events_to_media_events(events: Iterable[Dict[str, Any]]) -> List[MediaEvent]:
    """Transform network events into :class:`MediaEvent` objects.

    This helper understands the basic Media Collection payload shape where
    parameters are carried either as query string arguments or inside a JSON
    body.  Each network request may yield multiple media events if the body
    contains an ``events`` array.
    """

    media_events: List[MediaEvent] = []

    for event in events:
        body = event.get("bodyJSON")
        query = event.get("queryParams") or {}

        # If the payload contains an explicit ``events`` array iterate over
        # each entry.  Otherwise treat the request itself as a single event
        # whose parameters live in the query string/body top level.
        items: List[Dict[str, Any]]
        if isinstance(body, dict) and isinstance(body.get("events"), list):
            items = body.get("events", [])
        else:
            combined = {}
            if isinstance(body, dict):
                combined.update(body)
            combined.update(query)
            items = [combined]

        for item in items:
            params = dict(item.get("params", {}))
            # Merge query params for convenience when item represents the
            # entire request rather than an element of ``events``.
            if params is item and query:
                params.update(query)

            if params is not item:
                params.update(query)
                params.update({k: v for k, v in item.items() if k != "params"})

            event_type = params.get("s:event:type")
            session_id = (
                params.get("s:event:sid")
                or params.get("s:session:id")
                or params.get("sessionId")
            )
            if not event_type or not session_id:
                # Not an Adobe media event
                continue

            ts_device = _coerce_int(params.get("l:event:ts"))
            playhead = _coerce_float(params.get("l:event:playhead"))
            stream_type = params.get("s:stream:type")
            asset_type = params.get("s:asset:type")

            media_events.append(
                MediaEvent(
                    sessionId=session_id,
                    type=event_type,
                    tsDevice=ts_device,
                    playhead=playhead,
                    streamType=stream_type,
                    assetType=asset_type,
                    params=params,
                )
            )

    return media_events

