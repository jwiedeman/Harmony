from __future__ import annotations

"""High level ingestion helpers.

This module provides convenience functions that tie together the network
parsers and the :class:`~backend.unified.UnifiedRequest` model.  The helpers
accept either an open file object or a filesystem path, automatically detect
the log format (HAR, ``.chlsj`` or ``.chls``) and return a list of
:class:`UnifiedRequest` instances ready for further analysis.
"""

from typing import IO, Any, List

from .parsers import parse_network_file
from .unified import UnifiedRequest, to_unified_requests


def ingest_file(file_obj: IO[Any], filename: str | None = None) -> List[UnifiedRequest]:
    """Read a network log from ``file_obj`` and return unified requests.

    Parameters
    ----------
    file_obj:
        File-like object positioned at the beginning of a network capture.
    filename:
        Optional filename used for format detection and traceability.

    Returns
    -------
    list of :class:`UnifiedRequest`
        Normalised request objects produced from the network log.
    """

    events = parse_network_file(file_obj, filename)
    return to_unified_requests(events)


def ingest_path(path: str) -> List[UnifiedRequest]:
    """Read a network log from ``path`` and return unified requests."""

    # Open in binary mode so the underlying parser can decide how to decode
    # the contents (text vs binary ``.chls`` sessions).
    with open(path, "rb") as fh:
        return ingest_file(fh, path)


__all__ = ["ingest_file", "ingest_path"]
