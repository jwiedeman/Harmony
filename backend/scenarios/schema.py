from __future__ import annotations

"""Pydantic models describing the Heartbeat scenario DSL.

The real Harmony Heartbeat+ project contains a rich domain specific language
for expressing validation scenarios.  This module implements a very small
subset of that language so unit tests can parse and reason about scenarios
without depending on the full production implementation.

Only a handful of fields from the specification are supported.  Additional
fields can be added incrementally as the validator evolves.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PingRequirement(BaseModel):
    """Cadence and tolerance configuration for ping validation."""

    cadenceSec: float = Field(..., gt=0, description="Expected cadence in seconds")
    toleranceSec: float = Field(0, ge=0, description="Allowed deviation in seconds")
    minCount: Optional[int] = Field(
        None, ge=0, description="Minimum number of pings expected"
    )


class WithinMsOf(BaseModel):
    """Relative timing constraint used by event conditions."""

    after: Optional[str] = None
    before: Optional[str] = None
    lte: Optional[int] = Field(None, ge=0)
    gte: Optional[int] = Field(None, ge=0)


class EventCondition(BaseModel):
    """Single expected media event within a scenario."""

    type: str
    after: Optional[str] = None
    withinMsOf: Optional[WithinMsOf] = None
    requirePings: Optional[PingRequirement] = None


class ScenarioConstraints(BaseModel):
    """Global constraints applied across the scenario."""

    mainPing: Optional[PingRequirement] = None
    adPing: Optional[PingRequirement] = None
    livePlayheadMode: bool = False


class ParamRule(BaseModel):
    """Rules asserting the presence of parameters on events."""

    on: Literal["All"] | str
    require: List[str] = Field(default_factory=list)


class Scenario(BaseModel):
    """Top level scenario description."""

    name: str
    streamType: Optional[Literal["vod", "live", "linear"]] = None
    expect: List[EventCondition] = Field(..., min_length=1)
    constraints: ScenarioConstraints = Field(default_factory=ScenarioConstraints)
    paramRules: List[ParamRule] = Field(default_factory=list)


__all__ = [
    "Scenario",
    "EventCondition",
    "PingRequirement",
    "ScenarioConstraints",
    "ParamRule",
]
