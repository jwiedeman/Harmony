"""Utility helpers for parsing network logs.

This module exposes convenience wrappers around the individual HAR and
Charles ``.chlsj`` parsers.  The :func:`parse_network_file` function attempts to
select an appropriate parser based on a filename's extension or, when the
extension is unknown, by sniffing the file contents.
"""
from __future__ import annotations

import io
import json
import os
from typing import IO, Any, Dict, List

from .har_parser import parse_har
from .chlsj_parser import parse_chlsj
from .chls_parser import parse_chls


def _looks_like_json(text: str) -> bool:
    """Return True if ``text`` appears to be JSON."""

    return text.lstrip().startswith("{") or text.lstrip().startswith("[")


def parse_network_file(file_obj: IO[Any], filename: str | None = None) -> List[Dict[str, Any]]:
    """Parse a network log from ``file_obj``.

    Parameters
    ----------
    file_obj:
        IO object positioned at the start of the log contents.
    filename:
        Optional name of the uploaded file.  The extension helps determine which
        parser to use but is not strictly required when the content can be
        sniffed.

    Returns
    -------
    list of dict
        Network events in the common ``NetworkEvent`` structure used
        throughout Harmony.
    """

    ext = os.path.splitext(filename or "")[1].lower()
    if ext == ".har":
        return parse_har(file_obj, filename)
    if ext == ".chlsj":
        return parse_chlsj(file_obj, filename)
    if ext == ".chls":
        return parse_chls(file_obj, filename)

    # Extension unknown – attempt to sniff the contents.  Read the full payload
    # into memory so it can be wrapped in the appropriate IO type for the
    # underlying parser functions.
    content = file_obj.read()
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            # Binary data that isn't valid UTF-8 is assumed to be a Charles
            # ``.chls`` session.  ``parse_chls`` will raise a helpful error if
            # the CLI is unavailable.
            return parse_chls(io.BytesIO(content), filename)
    else:
        text = content

    if _looks_like_json(text):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Unsupported file content: invalid JSON") from exc

        # ``.har`` files store entries under ``log.entries`` while ``.chlsj``
        # exports may place them at the top level or under ``log``.
        if isinstance(data, dict) and isinstance(data.get("log"), dict) and isinstance(
            data["log"].get("entries"), list
        ):
            return parse_har(io.StringIO(text), filename)
        if isinstance(data, dict) and isinstance(data.get("entries"), list):
            return parse_chlsj(io.StringIO(text), filename)
        # Fallback to the HAR parser for any other JSON structure – it will
        # surface a meaningful error if the shape is incompatible.
        return parse_har(io.StringIO(text), filename)

    # Non-JSON text is treated as a binary Charles session.
    if isinstance(content, bytes):
        return parse_chls(io.BytesIO(content), filename)
    raise ValueError(f"Unsupported file type: {ext}")


__all__ = ["parse_network_file", "parse_har", "parse_chlsj", "parse_chls"]

