# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import pytest

from ansys.simai.core.errors import InvalidArguments


def test_get_geomai_training_data_by_id(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/training-data/td-123",
        json={"id": "td-123", "name": "My Training Data"},
        status_code=200,
    )
    td = simai_client.geomai.training_data.get(id="td-123")
    assert td.id == "td-123"
    assert td.name == "My Training Data"


def test_get_geomai_training_data_by_name(simai_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/geomai/training-data/name/My%20Training%20Data",
        json={"id": "td-456", "name": "My Training Data"},
        status_code=200,
    )
    td = simai_client.geomai.training_data.get(name="My Training Data")
    assert td.id == "td-456"
    assert td.name == "My Training Data"


def test_get_geomai_training_data_invalid_arguments(simai_client):
    with pytest.raises(InvalidArguments) as e:
        simai_client.training_data.get()
    assert str(e.value) == "Either 'id' or 'name' argument must be specified."

    with pytest.raises(InvalidArguments) as e:
        simai_client.training_data.get(id="td-123", name="My Training Data")
    assert str(e.value) == "Cannot specify both 'id' and 'name' arguments."
