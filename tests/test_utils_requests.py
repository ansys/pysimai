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

import pytest
import requests
from ansys.simai.core.errors import ApiClientError, SimAIError
from ansys.simai.core.utils.requests import handle_http_errors, handle_response
from requests.models import Response


def test_handle_http_errors(mocker):
    response_json_mock = mocker.patch("requests.models.Response.json")
    raise_for_status_mock = mocker.patch("requests.models.Response.raise_for_status")

    # Error without json body
    raise_for_status_mock.side_effect = requests.exceptions.HTTPError(Response())
    response_json_mock.side_effect = ValueError()

    with pytest.raises(SimAIError):
        handle_http_errors(Response())

    # Error with json body
    raise_for_status_mock.side_effect = requests.exceptions.HTTPError(Response())
    response_json_mock.side_effect = None
    response_json_mock.return_value = {"status": "rekt"}

    with pytest.raises(SimAIError, match="rekt"):
        handle_http_errors(Response())


def test_handle_response(mocker):
    mocker.patch("ansys.simai.core.utils.requests.handle_http_errors")
    response_json_mock = mocker.patch("requests.models.Response.json")

    # JSON response -> return json
    response_json_mock.return_value = {"status": "succeeding"}
    assert handle_response(Response(), return_json=True) == {"status": "succeeding"}

    # Non json response -> return response
    assert isinstance(handle_response(Response(), return_json=False), Response)

    # Malformed JSON -> error
    response_json_mock.side_effect = ValueError
    with pytest.raises(ApiClientError):
        handle_response(Response(), return_json=True)
