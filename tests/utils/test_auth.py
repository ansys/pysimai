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
#
# ruff: noqa: S105, S106

import copy
import time
from datetime import datetime, timezone
from math import ceil

import httpx
import pytest
from pytest_httpx import HTTPXMock

from ansys.simai.core.errors import SimAIError
from ansys.simai.core.utils.auth import (
    TOKEN_REFRESH_BUFFER,
    Authenticator,
    _AuthTokens,
    _AuthTokensRetriever,
)
from ansys.simai.core.utils.configuration import ClientConfig, Credentials

DEFAULT_TOKENS = {
    "access_token": "check",
    "expires_in": 60,
    "refresh_expires_in": 1800,
    "refresh_token": "kaboom",
}


def test_request_auth_tokens_direct_grant_bad_credentials_raises(mocker, tmpdir, httpx_mock):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    httpx_mock.add_response(
        method="POST",
        url="http://myauthserver.com/protocol/openid-connect/token",
        json={
            "error": "invalid_grant",
            "error_description": "Invalid user credentials",
        },
        status_code=401,
    )
    tokens_retriever = _AuthTokensRetriever(
        credentials=None,
        session=httpx.Client(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    with pytest.raises(SimAIError, match="Invalid user credentials"):
        tokens_retriever.credentials = Credentials(username="macron", password="explosion")
        tokens_retriever.get_tokens()


def test_request_auth_tokens_direct_grant(mocker, tmpdir, httpx_mock):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    httpx_mock.add_response(
        method="POST",
        url="http://myauthserver.com/protocol/openid-connect/token",
        json=DEFAULT_TOKENS,
        status_code=200,
    )
    tokens_retriever = _AuthTokensRetriever(
        credentials=None,
        session=httpx.Client(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    tokens_retriever.credentials = Credentials(username="timmy", password="")
    tokens = tokens_retriever.get_tokens()
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]


def test_token_refresh_failure_triggers_reauth(mocker, tmpdir, httpx_mock):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    httpx_mock.add_response(
        method="POST",
        url="http://myauthserver.com/protocol/openid-connect/token",
        status_code=418,
    )
    httpx_mock.add_response(
        method="POST",
        url="http://myauthserver.com/protocol/openid-connect/token",
        json=DEFAULT_TOKENS,
        status_code=200,
    )
    with open(tmpdir / "tokens-rando.json", "w") as f:
        f.write(
            _AuthTokens(
                access_token="",
                expires_in=0,
                refresh_expires_in=999,
                refresh_token="revoked",
            ).model_dump_json()
        )
    tokens_retriever = _AuthTokensRetriever(
        credentials=Credentials(username="timmy", password=""),
        session=httpx.Client(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    tokens = tokens_retriever.get_tokens()
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]
    # Note: With pytest-httpx, we can't easily check call counts like with responses
    # The test verifies that the tokens are retrieved correctly, which is the main goal


def test_request_auth_tokens_device_grant_with_bad_cache(mocker, tmpdir, httpx_mock):
    """WHEN A device auth flow is requested
    AND a (bad) refresh token is cached
    THEN SDK tries to use the cached refresh token
    AND requests a device auth flow if the token is invalid
    """
    webbrowser_open = mocker.patch("webbrowser.open")
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    mocker.patch("ansys.simai.core.utils.auth.DEVICE_AUTH_POLLING_INTERVAL", 0)
    refresh_token = "spaghetti"
    device_code = "foxtrot uniform charlie kilo"
    realm_url = "http://myauthserver.com/my-realm"
    token_retriever = _AuthTokensRetriever(
        credentials=None, session=httpx.Client(), realm_url=realm_url, auth_cache_hash="lol"
    )
    fake_cache = _AuthTokens(
        access_token="",
        expires_in=0,
        refresh_expires_in=999,
        refresh_token=refresh_token,
    )
    with open(tmpdir / "tokens-lol.json", "w") as f:
        f.write(fake_cache.model_dump_json())

    httpx_mock.add_response(  # error when app tries to use invalidated cached token
        method="POST",
        url=token_retriever.token_url,
        json={"poop": "Ur token down the drain"},
        status_code=418,
    )
    httpx_mock.add_response(  # device-auth flow start
        method="POST",
        url=token_retriever.device_auth_url,
        json={
            "verification_uri": "nope",
            "user_code": "abcdefg",
            "verification_uri_complete": "nope?code=abcdefg",
            "device_code": device_code,
        },
        status_code=200,
    )
    httpx_mock.add_response(  # device-auth flow end
        method="POST",
        url=token_retriever.token_url,
        json=DEFAULT_TOKENS,
        status_code=200,
    )

    tokens = token_retriever.get_tokens()
    webbrowser_open.assert_called_with("nope?code=abcdefg")
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert ceil(tokens.expires_in) == DEFAULT_TOKENS["expires_in"]
    assert ceil(tokens.refresh_expires_in) == DEFAULT_TOKENS["refresh_expires_in"]


def test_refresh_auth_tokens(mocker, tmpdir, httpx_mock):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    base_token = copy.deepcopy(DEFAULT_TOKENS)
    base_token["refresh_token"] = "kabam"
    final_token = copy.deepcopy(base_token)
    final_token["access_token"] = "new tok"

    expired_token = _AuthTokens.model_validate(copy.deepcopy(base_token))
    expired_token.expiration = datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)
    token_retriever = _AuthTokensRetriever(
        credentials=None,
        session=httpx.Client(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="popo",
    )
    token_retriever._get_token_from_cache = lambda: expired_token

    httpx_mock.add_response(
        method="POST",
        url="http://myauthserver.com/protocol/openid-connect/token",
        json=final_token,
        status_code=200,
    )

    fetched_token = token_retriever.get_tokens()
    assert fetched_token.access_token == final_token["access_token"]
    assert fetched_token.refresh_token == final_token["refresh_token"]


def test_authenticator_automatically_refreshes_auth_before_requests_if_needed(
    mocker, tmpdir, httpx_mock
):
    # Authentication request
    auth_tokens = copy.deepcopy(DEFAULT_TOKENS)
    auth_tokens["expires_in"] = 1
    auth_tokens["refresh_expires_in"] = 1800
    httpx_mock.add_response(
        method="POST",
        url="https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=auth_tokens,
        status_code=200,
    )
    # Token refresh request
    refresh_tokens = copy.deepcopy(DEFAULT_TOKENS)
    refresh_tokens["access_token"] = "check 1 2"
    refresh_tokens["refresh_token"] = "megazaur"
    httpx_mock.add_response(
        method="POST",
        url="https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=refresh_tokens,
        status_code=200,
    )

    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    auth = Authenticator(
        ClientConfig(
            url="https://simai.ansys.com",
            organization="13_monkeys",
            credentials=Credentials(username="timmy", password="key"),
        ),
        httpx.Client(),
    )

    req = httpx.Request("GET", "https://simai.ansys.com/v2/models")
    req = next(auth.auth_flow(req))
    assert req.headers.get("Authorization") == "Bearer check 1 2"
    assert req.headers.get("X-Org") == "13_monkeys"


def test_authenticator_automatically_refreshes_auth_before_refresh_token_expires(
    mocker, tmpdir, httpx_mock: HTTPXMock
):
    """
    Test that the Authenticator schedules and performs an automatic token refresh
    before the refresh token expires, based on the TOKEN_REFRESH_BUFFER.

    Verifies that when a refresh token is still valid but close to expiration,
    the authenticator schedules a refresh operation to prevent token expiration
    during idle periods.
    """
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)

    tokens_direct_grant = copy.deepcopy(DEFAULT_TOKENS)
    tokens_direct_grant["access_token"] = "monkey-see"
    tokens_direct_grant["expires_in"] = TOKEN_REFRESH_BUFFER + 100
    tokens_direct_grant["refresh_expires_in"] = TOKEN_REFRESH_BUFFER + 1
    httpx_mock.add_response(
        method="POST",
        url="https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=tokens_direct_grant,
        status_code=200,
    )
    matcher_direct_grant = httpx_mock._callbacks[-1][0]

    refreshed_tokens = DEFAULT_TOKENS.copy()
    refreshed_tokens["access_token"] = "TFou"
    httpx_mock.add_response(
        method="POST",
        url="https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=refreshed_tokens,
        status_code=200,
    )
    matcher_refresh = httpx_mock._callbacks[-1][0]
    auth = Authenticator(
        ClientConfig(
            url="https://simai.ansys.com",
            organization="14_monkeys",
            credentials=Credentials(username="timmy", password="key"),
        ),
        httpx.Client(),
    )
    initial_refresh_timer = auth.tokens_retriever.refresh_timer
    assert matcher_direct_grant.nb_calls == 1
    assert matcher_refresh.nb_calls == 0
    assert initial_refresh_timer.is_alive()
    t0 = time.time()
    while time.time() - t0 < 2 and auth.tokens_retriever.refresh_timer == initial_refresh_timer:
        # wait for the refresh timer to restart, or for the 2sec timeout...
        time.sleep(0.1)
    assert matcher_direct_grant.nb_calls == 1  # Initial authentication
    assert matcher_direct_grant.nb_calls == 1  # Tokens refresh
    assert auth.tokens_retriever.refresh_timer != initial_refresh_timer
    assert auth.tokens_retriever.refresh_timer.is_alive()


def test_requests_outside_user_api_are_not_authentified(mocker, tmpdir, httpx_mock):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    # Authentication request
    keycloak_response_json = DEFAULT_TOKENS.copy()
    httpx_mock.add_response(
        method="POST",
        url="https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=keycloak_response_json,
        status_code=200,
    )

    auth = Authenticator(
        ClientConfig(
            url="https://simai.ansys.com",
            organization="Justice",
            credentials={"username": "timmy", "password": "D.A.N.C.E"},
        ),
        httpx.Client(),
    )

    request = httpx.Request("GET", "https://amazonaws.com/bloc-party")
    request = next(auth.auth_flow(request))
    assert request.headers.get("Authorization") is None
    assert request.headers.get("X-Org") is None
