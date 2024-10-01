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

import os
import platform
import time
from pathlib import Path

import pytest

from ansys.simai.core.utils.files import get_cache_dir


@pytest.mark.skipif(
    platform.system() != "Linux",
    reason="This test uses XDG_CACHE_HOME to avoid touching the host system",
)
def test_get_cache_dir_linux(tmpdir, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmpdir))
    cache_dir = get_cache_dir()
    expected_cache_dir = Path(tmpdir).absolute() / "ansys" / "pysimai"
    assert cache_dir.absolute() == expected_cache_dir
    old_file = cache_dir / "old"
    new_file = cache_dir / "new"
    new_file.touch()
    old_file.touch()
    now = time.time()
    a_year_ago = now - 30000000
    os.utime(old_file, times=(now, a_year_ago))
    cache_dir = get_cache_dir()
    assert new_file.is_file()
    assert not old_file.is_file()
