"""Utility helpers for parsing network logs.

This module exposes convenience wrappers around the individual HAR and
Charles ``.chlsj`` parsers.  The :func:`parse_network_file` function selects the
appropriate parser based on a filename's extension so callers only need to
provide the file object and original name.
"""
from __future__ import annotations

import os
from typing import IO, Any, Dict, List

from .har_parser import parse_har
from .chlsj_parser import parse_chlsj
from .chls_parser import parse_chls


def parse_network_file(file_obj: IO[Any], filename: str) -> List[Dict[str, Any]]:
    """Parse a network log from ``file_obj``.

    Parameters
    ----------
    file_obj:
        IO object positioned at the start of the log contents.
    filename:
        Name of the uploaded file.  The extension determines which parser to
        use.  ``.har`` files are treated as HTTP Archive logs while ``.chlsj``
        files are interpreted as Charles sessions.  The binary ``.chls`` format
        is converted using the Charles CLI when available.

    Returns
    -------
    list of dict
        Network events in the common ``NetworkEvent`` structure used
        throughout Harmony.
    """

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".har":
        return parse_har(file_obj)
    if ext == ".chlsj":
        return parse_chlsj(file_obj)
    if ext == ".chls":
        return parse_chls(file_obj)
    raise ValueError(f"Unsupported file type: {ext}")


__all__ = ["parse_network_file", "parse_har", "parse_chlsj", "parse_chls"]

