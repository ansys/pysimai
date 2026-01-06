# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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


import httpcore
import httpx
import pytest
from pydantic import HttpUrl
from pytest_httpx import HTTPXMock

from ansys.simai.core import SimAIClient
from ansys.simai.core.errors import ApiClientError, NotFoundError

from .conftest import disable_http_retry


def test_construct_default_url():
    """WHEN No URL is passed to SimAIClient
    THEN A default one is used
    """
    client = SimAIClient(
        no_sse_connection=True,
        _disable_authentication=True,
        skip_version_check=True,
        organization="ExtraBanane",
    )
    assert client._api._url_prefix == HttpUrl("https://api.simai.ansys.com/v2/")


def test_retry_on_5XX(api_client, httpx_mock: HTTPXMock):
    url = "https://try.me/"
    httpx_mock.add_response(method="GET", url=url, status_code=503)
    httpx_mock.add_response(method="GET", url=url, status_code=504)
    httpx_mock.add_response(method="GET", url=url, status_code=200, json={"wat": "hyperdrama"})
    resp = api_client._get(url)
    assert resp == {"wat": "hyperdrama"}


def test_404_response_raises_not_found_error(api_client, httpx_mock: HTTPXMock):
    """WHEN ApiClient gets a 404 response
    THEN a NotFoundError is raised
    """
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/expected_format",
        json={"message": "beep-boop"},
        status_code=404,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://test.test/only_status_format",
        json={"status": "not found"},
        status_code=404,
    )
    httpx_mock.add_response(method="GET", url="https://test.test/no_content", status_code=404)

    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("expected_format")
    assert exc_info.value.args[0] == "beep-boop"
    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("only_status_format")
    assert exc_info.value.args[0] == "not found"
    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("no_content")
    assert exc_info.value.args[0] == "Not Found"


@pytest.mark.parametrize(
    "code, reason",
    [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        # (404, "Not Found"), # raises NotFoundError instead # noqa: ERA001
        (405, "Method Not Allowed"),
        (500, "Internal Server Error"),
        (501, "Not Implemented"),
        (502, "Bad Gateway"),
    ],
)
def test_4XX_5XX_responses_raise_api_client_error_no_json(
    api_client, httpx_mock: HTTPXMock, code, reason
):
    """WHEN ApiClient gets a 4XX or 5XX response without details in json
    THEN a ApiClientError is raised with the code and reason
    """
    httpx_mock.add_response(method="GET", url=f"https://test.test/{code}", status_code=code)
    with disable_http_retry(api_client, "https://test.test/"):
        with pytest.raises(ApiClientError) as exc_info:
            api_client._get(f"{code}")
        assert exc_info.value.args[0] == f"{code} {reason}"


@pytest.mark.parametrize(
    "json, message",
    [
        ({"errors": {"beep": "boop"}}, "{'beep': 'boop'}"),
        ({"message": "tomato"}, "tomato"),
        (
            {"status": "I'm sorry Dave, I'm afraid I can't do that"},
            "I'm sorry Dave, I'm afraid I can't do that",
        ),
        (None, "Bad Request"),
    ],
)
def test_4XX_5XX_responses_raise_api_client_error_with_json(api_client, httpx_mock, json, message):
    """WHEN ApiClient gets a 4XX or 5XX response without details in json
    THEN a ApiClientError is raised with the code and message from the json or fallback
    """
    httpx_mock.add_response(
        method="GET", url="https://test.test/errors", json=json, status_code=400
    )

    with pytest.raises(ApiClientError) as exc_info:
        api_client._get("errors")
    assert exc_info.value.args[0] == f"400 {message}"


def test_use_system_proxies(mocker):
    """WHEN ApiClient is initialized on a system with default proxies
    THEN the system proxies are used
    """
    proxy_url = "https://bonzibuddy.org"
    mocker.patch(
        "httpx._utils.getproxies",
        return_value={"http": proxy_url},
    )

    client = SimAIClient(
        no_sse_connection=True,
        _disable_authentication=True,
        skip_version_check=True,
        organization="ExtraBanane",
    )
    transport = client._api._session._transport_for_url(httpx.URL("http://popo.org"))
    assert transport._sync_transport._pool._proxy_url == httpcore.URL(proxy_url)


def test_use_user_provided_proxies(mocker):
    """WHEN ApiClient is initialized with a specific https_proxy
    THEN the specific proxy is used (system proxies are ignored), the url is normalized
    """
    mocker.patch(
        "httpx._utils.getproxies",
        return_value={"https": "https://bonzibuddy.org"},
    )

    client = SimAIClient(
        no_sse_connection=True,
        _disable_authentication=True,
        skip_version_check=True,
        organization="ExtraBanane",
        https_proxy="https://😛.com",
    )
    transport = client._api._session._transport_for_url(httpx.URL("https://popo.org"))
    assert transport._sync_transport._pool._proxy_url == httpcore.URL("https://xn--528h.com")
