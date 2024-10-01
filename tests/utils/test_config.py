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

import platform
from pathlib import Path

import pytest

import ansys.simai.core.errors as err
from ansys.simai.core.utils.config_file import _scan_defaults_config_paths, get_config


@pytest.mark.skipif(platform.system() == "Windows", reason="XDG_CONFIG_HOME is for unix systems")
def test_xdg_config_home_is_respected(monkeypatch, tmpdir):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmpdir))
    config_file_path = Path(tmpdir) / "ansys_simai.conf"
    config_file_path.touch()
    assert _scan_defaults_config_paths() == config_file_path


def test_get_config_invalid_path():
    with pytest.raises(err.ConfigurationNotFoundError):
        get_config(path="/")


def test_get_config_invalid_profile(tmpdir):
    path_config = Path(tmpdir) / "config"
    with open(path_config, "w+") as f:
        f.write("[default]\n")
        f.flush()
        with pytest.raises(err.InvalidConfigurationError):
            get_config(profile="kaboom", path=path_config)


def test_get_config_ignore_missing(mocker):
    mocker.patch(
        "ansys.simai.core.utils.config_file._scan_defaults_config_paths",
        return_value=None,
    )
    config = get_config(ignore_missing=True, organization="kangarooooo")
    assert config == {"organization": "kangarooooo"}
