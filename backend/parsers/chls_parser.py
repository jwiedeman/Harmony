import os
import shutil
import subprocess
import tempfile
from typing import BinaryIO, Dict, List

from .har_parser import parse_har


def parse_chls(file_obj: BinaryIO) -> List[Dict[str, object]]:
    """Parse a Charles ``.chls`` session file.

    The binary ``.chls`` format must be converted to HAR or ``.chlsj`` using the
    Charles CLI.  This function attempts the conversion and then delegates to the
    HAR parser.  If the ``charles`` command is unavailable a ``RuntimeError`` is
    raised instructing the caller to supply a ``.har`` or ``.chlsj`` file
    instead.
    """
    charles = shutil.which("charles")
    if charles is None:
        raise RuntimeError(
            "Charles CLI ('charles') not found. Provide a .har or .chlsj file instead."
        )

    with tempfile.NamedTemporaryFile(suffix=".chls", delete=False) as src:
        src.write(file_obj.read())
        src_path = src.name
    with tempfile.NamedTemporaryFile(suffix=".har", delete=False) as dst:
        dst_path = dst.name

    try:
        subprocess.run([charles, "convert", src_path, dst_path], check=True, capture_output=True)
        with open(dst_path, "r", encoding="utf-8") as converted:
            return parse_har(converted)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="ignore") if e.stderr else ""
        raise RuntimeError(
            f"Failed to convert .chls using Charles CLI: {stderr.strip()}"
        ) from e
    finally:
        for path in (src_path, dst_path):
            try:
                os.remove(path)
            except OSError:
                pass
