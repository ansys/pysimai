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
from json import JSONDecodeError

import niquests
import pytest
from niquests.models import Response

from ansys.simai.core.errors import ApiClientError, SimAIError
from ansys.simai.core.utils.requests import handle_http_errors, handle_response


def test_handle_http_errors(mocker):
    response_json_mock = mocker.patch("niquests.models.Response.json")
    raise_for_status_mock = mocker.patch("niquests.models.Response.raise_for_status")

    # Error without json body
    raise_for_status_mock.side_effect = niquests.exceptions.HTTPError(Response())
    response_json_mock.side_effect = ValueError()

    with pytest.raises(SimAIError):
        handle_http_errors(Response())

    # Error with json body
    raise_for_status_mock.side_effect = niquests.exceptions.HTTPError(Response())
    response_json_mock.side_effect = None
    response_json_mock.return_value = {"status": "rekt"}

    with pytest.raises(SimAIError, match="rekt"):
        handle_http_errors(Response())


@pytest.mark.parametrize(
    "status_code, return_value, return_json",
    (
        (200, {"status": "succeeding"}, True),
        (200, {"status": "succeeding"}, False),
        (204, "Should be None", True),
    ),
)
def test_handle_response_success(mocker, status_code, return_value, return_json):
    mocker.patch("ansys.simai.core.utils.requests.handle_http_errors")
    mocker.patch.object(Response, "json", return_value=return_value)
    response = Response()
    response.status_code = status_code

    result = handle_response(response, return_json=return_json)

    if return_json is False:
        assert isinstance(result, Response)
    elif status_code == 204:
        assert result is None
    else:
        assert result == return_value


@pytest.mark.parametrize(
    "status_code, side_effect",
    (
        (200, JSONDecodeError("msg", "doc", 0)),
        (200, ValueError()),
    ),
)
def test_handle_response_raises(mocker, status_code, side_effect):
    mocker.patch("ansys.simai.core.utils.requests.handle_http_errors")
    mocker.patch("requests.models.Response.json", side_effect=side_effect)
    response = Response()
    response.status_code = status_code

    with pytest.raises(ApiClientError):
        handle_response(Response(), return_json=True)
