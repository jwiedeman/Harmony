from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MediaEvent(BaseModel):
    """Normalized representation of a single Adobe Media event.

    The fields are intentionally aligned with the Harmony Heartbeat+
    specification.  Only a subset of the eventual schema is implemented
    here so unit tests can exercise the parser without requiring the full
    state machine or timing engine.
    """

    sessionId: str = Field(..., description="Unique session identifier")
    type: str = Field(..., description="Event type such as play or ping")
    tsDevice: int = Field(..., description="Device timestamp in ms")
    playhead: float = Field(..., description="Playhead position in seconds")
    streamType: Optional[str] = Field(None, description="vod|live|linear")
    assetType: Optional[str] = Field(None, description="main|ad")
    params: Dict[str, Any] = Field(default_factory=dict, description="Raw parameters")

