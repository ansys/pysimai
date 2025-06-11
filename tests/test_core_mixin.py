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

from io import BytesIO

import pytest
import responses
from pydantic import HttpUrl
from responses import matchers

from ansys.simai.core import SimAIClient
from ansys.simai.core.errors import ApiClientError, NotFoundError


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


@responses.activate(registry=responses.registries.OrderedRegistry)
def test_retry_on_5XX(api_client):
    url = "https://try.me/"
    rsp1 = responses.add(responses.GET, url=url, status=503)
    rsp2 = responses.add(responses.GET, url=url, status=504)
    rsp3 = responses.add(responses.GET, url=url, status=200, json={"wat": "hyperdrama"})
    resp = api_client._get(url)
    assert resp == {"wat": "hyperdrama"}
    assert rsp1.call_count == 1
    assert rsp2.call_count == 1
    assert rsp3.call_count == 1


@responses.activate
def test_404_response_raises_not_found_error(api_client):
    """WHEN ApiClient gets a 404 response
    THEN a NotFoundError is raised
    """
    responses.add(
        responses.GET,
        "https://test.test/expected_format",
        json={"message": "beep-boop"},
        status=404,
    )
    responses.add(
        responses.GET,
        "https://test.test/only_status_format",
        json={"status": "not found"},
        status=404,
    )
    responses.add(responses.GET, "https://test.test/no_content", status=404)

    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("expected_format")
    assert exc_info.value.args[0] == "beep-boop"
    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("only_status_format")
    assert exc_info.value.args[0] == "not found"
    with pytest.raises(NotFoundError) as exc_info:
        api_client._get("no_content")
    assert exc_info.value.args[0] == "Not Found"


@responses.activate
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
def test_4XX_5XX_responses_raise_api_client_error_no_json(api_client, code, reason):
    """WHEN ApiClient gets a 4XX or 5XX response without details in json
    THEN a ApiClientError is raised with the code and reason
    """
    responses.add(responses.GET, f"https://test.test/{code}", status=code)

    with pytest.raises(ApiClientError) as exc_info:
        api_client._get(f"{code}")
    assert exc_info.value.args[0] == f"{code} {reason}"


@responses.activate
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
def test_4XX_5XX_responses_raise_api_client_error_with_json(api_client, json, message):
    """WHEN ApiClient gets a 4XX or 5XX response without details in json
    THEN a ApiClientError is raised with the code and message from the json or fallback
    """
    responses.add(responses.GET, "https://test.test/errors", json=json, status=400)

    with pytest.raises(ApiClientError) as exc_info:
        api_client._get("errors")
    assert exc_info.value.args[0] == f"400 {message}"


def test_use_system_proxies(mocker):
    """WHEN ApiClient is initialized on a system with default proxies
    THEN the system proxies are used
    """
    mocker.patch(
        "ansys.simai.core.api.mixin.getproxies",
        return_value={"grpc": "https://bonzibuddy.org"},
    )
    client = SimAIClient(
        no_sse_connection=True,
        _disable_authentication=True,
        skip_version_check=True,
        organization="ExtraBanane",
    )
    assert client._api._session.proxies == {"grpc": "https://bonzibuddy.org"}


def test_use_user_provided_proxies(mocker):
    """WHEN ApiClient is initialized with a specific https_proxy
    THEN the specific proxy is used (system proxies are ignored), the url is normalized
    """
    mocker.patch(
        "ansys.simai.core.api.mixin.getproxies",
        return_value={"grpc": "https://bonzibuddy.org"},
    )

    client = SimAIClient(
        no_sse_connection=True,
        _disable_authentication=True,
        skip_version_check=True,
        organization="ExtraBanane",
        https_proxy="https://😛.com",
    )
    assert client._api._session.proxies == {"https": "https://xn--528h.com/"}


@responses.activate
def test_upload_file_with_presigned_post_monitor_callback(mocker, api_client):
    presigned_post = {"fields": {"sandstorm": "TUTUTUUTUTU"}, "url": "https://leekspin.com/"}
    file = BytesIO(b"Hello World")
    file.name = "hello.txt"
    responses.add(
        responses.POST,
        "https://leekspin.com/",
        match=[
            matchers.multipart_matcher(
                data={
                    **presigned_post["fields"],
                },
                files={"file": ("hello.txt", file, "application/octet-stream")},
            )
        ],
        status=200,
    )
    monitor_values = []
    api_client.upload_file_with_presigned_post(
        file=file,
        presigned_post=presigned_post,
        monitor_callback=lambda x: monitor_values.append(x),
    )
    # Bigger than `file` because:
    # * the multipart encoding
    # * the other fields (`sandstorm`)
    assert monitor_values == [297]
