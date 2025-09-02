from __future__ import annotations

"""Parameter validation helpers for media events.

This module implements a lightweight validator that checks whether required
parameters are present on media events.  It is intentionally small in scope so
that unit tests can exercise the behaviour without relying on the full Harmony
Heartbeat+ implementation.
"""

from typing import Iterable, List

from .models import MediaEvent
from ..scenarios.schema import ParamRule


def validate_param_rules(events: Iterable[MediaEvent], rules: Iterable[ParamRule]) -> List[str]:
    """Validate parameter presence according to ``rules``.

    Parameters
    ----------
    events:
        Chronologically ordered :class:`MediaEvent` objects.
    rules:
        Iterable of :class:`ParamRule` objects describing which parameters must
        be present on which event types.  The special event type ``"All"``
        applies the rule to every event.

    Returns
    -------
    list of str
        Human readable violation messages describing any missing parameters.
    """

    violations: List[str] = []
    for event in events:
        for rule in rules:
            if rule.on != "All" and rule.on != event.type:
                continue
            for name in rule.require:
                value = event.params.get(name)
                if value in (None, ""):
                    violations.append(
                        f"{event.type} missing required parameter {name}"
                    )
    return violations


__all__ = ["validate_param_rules"]
