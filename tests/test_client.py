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

from pathlib import Path

import pytest
import responses

import ansys.simai.core.errors as err
from ansys.simai.core import SimAIClient


def test_client_creation_invalid_path():
    with pytest.raises(err.ConfigurationNotFoundError):
        SimAIClient.from_config(path="/")


def test_client_creation_invalid_config():
    with pytest.raises(err.InvalidConfigurationError):
        SimAIClient.from_config(path=Path(__file__).resolve())


@pytest.mark.parametrize(
    "local_ver,latest_ver,expected",
    [
        ("1.1.0", "1.1.1", "available."),
        ("1.0.9-rc8", "1.0.9", "available."),
        ("1.0.9", "1.9.0", "required."),
    ],
)
@responses.activate
def test_client_version_auto_warn(caplog, mocker, local_ver, latest_ver, expected):
    """WHEN the SDK version is slightly outdated compared to what the API responds
    THEN a warning is printed
    """
    mocker.patch(
        "ansys.simai.core.client.__version__",
        local_ver,
    )
    responses.add(
        responses.GET,
        "https://pypi.org/pypi/ansys-simai-core/json",
        json={"info": {"version": latest_ver}},
        status=200,
    )
    SimAIClient(
        url="https://test.test",
        organization="dummy",
        _disable_authentication=True,
        no_sse_connection=True,
        skip_version_check=False,
    )
    assert f"A new version of ansys-simai-core is {expected}" in caplog.text
