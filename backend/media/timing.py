from __future__ import annotations

"""Ping cadence validation helpers.

This module implements a very small portion of the timing engine described in
*Harmony Heartbeat+*.  It focuses solely on verifying the cadence of ``ping``
requests during main content and advertisement playback.  The goal is not to be
feature complete but to provide a lightweight utility that unit tests can
exercise.
"""

from typing import Iterable, List

from .models import MediaEvent


def validate_ping_cadence(
    events: Iterable[MediaEvent],
    main_cadence: float = 10.0,
    ad_cadence: float = 1.0,
    tolerance: float = 2.0,
) -> List[str]:
    """Validate ping intervals for main content and ad playback.

    Parameters
    ----------
    events:
        Chronologically ordered :class:`MediaEvent` objects belonging to a
        single session.
    main_cadence:
        Expected seconds between pings while main content is playing.
    ad_cadence:
        Expected seconds between pings while advertisements are playing.
    tolerance:
        Allowed deviation in seconds from the expected cadence.

    Returns
    -------
    list of str
        Human readable violation messages.  The list will be empty when all
        pings occur within the specified cadence and tolerance.
    """

    cad_main_ms = int(main_cadence * 1000)
    cad_ad_ms = int(ad_cadence * 1000)
    tol_ms = int(tolerance * 1000)

    current_asset: str | None = None  # 'main' or 'ad'
    expected_ts: int | None = None
    violations: List[str] = []

    for event in sorted(events, key=lambda e: e.tsDevice):
        t = event.type
        asset = event.assetType or event.params.get("s:asset:type")

        if t in {"play", "adStart"}:
            current_asset = "ad" if (asset == "ad" or t == "adStart") else "main"
            cadence_ms = cad_ad_ms if current_asset == "ad" else cad_main_ms
            expected_ts = event.tsDevice + cadence_ms
            continue

        if t == "ping" and current_asset is not None:
            cadence_ms = cad_ad_ms if current_asset == "ad" else cad_main_ms
            if expected_ts is not None:
                delta = event.tsDevice - expected_ts
                if abs(delta) > tol_ms:
                    if delta > 0:
                        violations.append(
                            f"missing ping before {event.tsDevice} (expected around {expected_ts})"
                        )
                    else:
                        violations.append(
                            f"early ping at {event.tsDevice} (expected around {expected_ts})"
                        )
            expected_ts = event.tsDevice + cadence_ms
            continue

        if t in {
            "pauseStart",
            "bufferStart",
            "adBreakStart",
            "adBreakComplete",
            "adComplete",
            "sessionEnd",
            "sessionComplete",
        }:
            current_asset = None
            expected_ts = None
            continue
        # Other event types are ignored.

    return violations


def compute_ping_integrity(
    events: Iterable[MediaEvent],
    main_cadence: float = 10.0,
    ad_cadence: float = 1.0,
    tolerance: float = 2.0,
) -> float:
    """Return the percentage of expected pings that occurred within tolerance.

    The function mirrors :func:`validate_ping_cadence` but instead of
    returning human readable violation messages it calculates a score in the
    range ``0`` – ``100``.  A score of ``100`` means every expected ping was
    observed within the configured tolerance while ``0`` indicates that none of
    the expected pings arrived on time.
    """

    cad_main_ms = int(main_cadence * 1000)
    cad_ad_ms = int(ad_cadence * 1000)
    tol_ms = int(tolerance * 1000)

    current_asset: str | None = None
    cadence_ms: int | None = None
    expected_ts: int | None = None
    expected = 0
    observed = 0

    for event in sorted(events, key=lambda e: e.tsDevice):
        t = event.type
        asset = event.assetType or event.params.get("s:asset:type")

        if t in {"play", "adStart"}:
            current_asset = "ad" if (asset == "ad" or t == "adStart") else "main"
            cadence_ms = cad_ad_ms if current_asset == "ad" else cad_main_ms
            expected_ts = event.tsDevice + cadence_ms
            continue

        if t == "ping" and current_asset is not None:
            if expected_ts is not None and cadence_ms is not None:
                # Account for any completely missing pings before this one.
                while event.tsDevice - expected_ts > tol_ms:
                    expected += 1
                    expected_ts += cadence_ms

                expected += 1
                if abs(event.tsDevice - expected_ts) <= tol_ms:
                    observed += 1
                expected_ts = event.tsDevice + cadence_ms
            continue

        if t in {
            "pauseStart",
            "bufferStart",
            "adBreakStart",
            "adBreakComplete",
            "adComplete",
            "sessionEnd",
            "sessionComplete",
        }:
            if expected_ts is not None and cadence_ms is not None:
                while event.tsDevice - expected_ts > tol_ms:
                    expected += 1
                    expected_ts += cadence_ms
            current_asset = None
            cadence_ms = None
            expected_ts = None
            continue
        # Other events are ignored.

    if expected == 0:
        return 100.0
    return observed / expected * 100.0


__all__ = ["validate_ping_cadence", "compute_ping_integrity"]
