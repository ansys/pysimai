# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import pathlib
import platform
import time
from typing import IO, TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ansys.simai.core.data.types import Path


def _expand_user_path(file_path: "Path") -> pathlib.Path:
    """Convert string inputs to ``Path`` and expand the user.

    This method supports paths starting with ``~`` on Linux.
    """
    return pathlib.Path(str(file_path)).expanduser()


def file_path_to_obj_file(file_path: "Path", mode: str) -> IO[Any]:
    """Take a file path and return a file-object opened in the given mode."""
    file_path = _expand_user_path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Opening file {file_path}")
    return open(file_path, mode=mode)  # noqa: SIM115


def get_cache_dir() -> pathlib.Path:
    system = platform.system()
    if system == "Windows":
        cache_dir = pathlib.Path(os.getenv("APPDATA", "~")) / "Ansys/cache"
    elif system == "Linux":
        cache_dir = pathlib.Path(os.getenv("XDG_CACHE_HOME", "~/.cache")) / "ansys"
    elif system == "Darwin":
        cache_dir = pathlib.Path("~/Library/Caches/Ansys")
    else:
        raise RuntimeError(f"Unknown OS: {system}")
    cache_dir = cache_dir.expanduser()
    cache_dir.mkdir(exist_ok=True, parents=True)
    a_week_ago = time.time() - 7 * 86400
    for cache_entry in pathlib.Path(cache_dir).glob("*"):
        if cache_entry.is_file():
            itemTime = cache_entry.stat().st_mtime
            if itemTime < a_week_ago:
                cache_entry.unlink()
    return cache_dir
