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
#
# ruff: noqa: S105, S106

import copy
import json
import time
from datetime import datetime, timezone
from math import ceil

import niquests
import pytest
import responses
from responses.matchers import urlencoded_params_matcher

from ansys.simai.core.errors import SimAIError
from ansys.simai.core.utils.auth import Authenticator, _AuthTokens, _AuthTokensRetriever
from ansys.simai.core.utils.configuration import ClientConfig, Credentials

DEFAULT_TOKENS = {
    "access_token": "check",
    "expires_in": 60,
    "refresh_expires_in": 1800,
    "refresh_token": "kaboom",
}


@responses.activate
def test_request_auth_tokens_direct_grant_bad_credentials_raises(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    responses.add(
        responses.POST,
        "http://myauthserver.com/protocol/openid-connect/token",
        json={
            "error": "invalid_grant",
            "error_description": "Invalid user credentials",
        },
        status=401,
        match=[
            urlencoded_params_matcher(
                {
                    "username": "macron",
                    "password": "explosion",
                    "client_id": "sdk",
                    "grant_type": "password",
                    "scope": "openid",
                }
            )
        ],
    )
    tokens_retriever = _AuthTokensRetriever(
        credentials=None,
        session=niquests.Session(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    with pytest.raises(SimAIError, match="Invalid user credentials"):
        tokens_retriever.credentials = Credentials(username="macron", password="explosion")
        tokens_retriever.get_tokens()


@responses.activate
def test_request_auth_tokens_direct_grant(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    responses.add(
        responses.POST,
        "http://myauthserver.com/protocol/openid-connect/token",
        json=DEFAULT_TOKENS,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "username": "timmy",
                    "client_id": "sdk",
                    "grant_type": "password",
                    "scope": "openid",
                }
            )
        ],
    )
    tokens_retriever = _AuthTokensRetriever(
        credentials=None,
        session=niquests.Session(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    tokens_retriever.credentials = Credentials(username="timmy", password="")
    tokens = tokens_retriever.get_tokens()
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]


@responses.activate
def test_token_refresh_failure_triggers_reauth(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    resps_refresh = responses.add(
        responses.POST,
        "http://myauthserver.com/protocol/openid-connect/token",
        status=418,
        match=[
            urlencoded_params_matcher(
                {"client_id": "sdk", "grant_type": "refresh_token", "refresh_token": "revoked"}
            )
        ],
    )
    resps_direct_grant = responses.add(
        responses.POST,
        "http://myauthserver.com/protocol/openid-connect/token",
        json=DEFAULT_TOKENS,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "username": "timmy",
                    "client_id": "sdk",
                    "grant_type": "password",
                    "scope": "openid",
                }
            )
        ],
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
        session=niquests.Session(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="rando",
    )
    tokens = tokens_retriever.get_tokens()
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]
    assert resps_refresh.call_count == 1
    assert resps_direct_grant.call_count == 1


@responses.activate
def test_request_auth_tokens_device_grant_with_bad_cache(mocker, tmpdir):
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
        credentials=None, session=niquests.Session(), realm_url=realm_url, auth_cache_hash="lol"
    )
    fake_cache = _AuthTokens(
        access_token="",
        expires_in=0,
        refresh_expires_in=999,
        refresh_token=refresh_token,
    )
    with open(tmpdir / "tokens-lol.json", "w") as f:
        json.dump(fake_cache.model_dump_json(), f)

    responses.add(  # error when app tries to use invalidated cached token
        responses.POST,
        token_retriever.token_url,
        json={"poop": "Ur token down the drain"},
        status=418,
        match=[
            urlencoded_params_matcher(
                {
                    "client_id": "sdk",
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            )
        ],
    )
    responses.add(  # device-auth flow start
        responses.POST,
        token_retriever.device_auth_url,
        json={
            "verification_uri": "nope",
            "user_code": "abcdefg",
            "verification_uri_complete": "nope?code=abcdefg",
            "device_code": device_code,
        },
        status=200,
        match=[urlencoded_params_matcher({"client_id": "sdk", "scope": "openid"})],
    )
    responses.add(  # device-auth flow end
        responses.POST,
        token_retriever.token_url,
        json=DEFAULT_TOKENS,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": "sdk",
                    "device_code": device_code,
                }
            )
        ],
    )

    tokens = token_retriever.get_tokens()
    webbrowser_open.assert_called_with("nope?code=abcdefg")
    assert tokens.access_token == DEFAULT_TOKENS["access_token"]
    assert tokens.refresh_token == DEFAULT_TOKENS["refresh_token"]
    assert ceil(tokens.expires_in) == DEFAULT_TOKENS["expires_in"]
    assert ceil(tokens.refresh_expires_in) == DEFAULT_TOKENS["refresh_expires_in"]


@responses.activate
def test_refresh_auth_tokens(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    base_token = copy.deepcopy(DEFAULT_TOKENS)
    base_token["refresh_token"] = "kabam"
    final_token = copy.deepcopy(base_token)
    final_token["access_token"] = "new tok"

    expired_token = _AuthTokens.model_validate(copy.deepcopy(base_token))
    expired_token.expiration = datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)
    token_retriever = _AuthTokensRetriever(
        credentials=None,
        session=niquests.Session(),
        realm_url="http://myauthserver.com",
        auth_cache_hash="popo",
    )
    token_retriever._get_token_from_cache = lambda: expired_token

    responses.add(
        responses.POST,
        "http://myauthserver.com/protocol/openid-connect/token",
        json=final_token,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "client_id": "sdk",
                    "grant_type": "refresh_token",
                    "refresh_token": "kabam",
                }
            )
        ],
    )

    fetched_token = token_retriever.get_tokens()
    assert fetched_token.access_token == final_token["access_token"]
    assert fetched_token.refresh_token == final_token["refresh_token"]


@responses.activate
def test_authenticator_automatically_refreshes_auth_before_requests_if_needed(mocker, tmpdir):
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        # Authentication request
        auth_tokens = copy.deepcopy(DEFAULT_TOKENS)
        auth_tokens["expires_in"] = 1
        auth_tokens["refresh_expires_in"] = 1800
        rsps.add(
            responses.POST,
            "https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
            json=auth_tokens,
            status=200,
            match=[
                urlencoded_params_matcher(
                    {
                        "client_id": "sdk",
                        "grant_type": "password",
                        "scope": "openid",
                        "username": "timmy",
                        "password": "key",
                    }
                )
            ],
        )
        # Token refresh request
        refresh_tokens = copy.deepcopy(DEFAULT_TOKENS)
        refresh_tokens["access_token"] = "check 1 2"
        refresh_tokens["refresh_token"] = "megazaur"
        rsps.add(
            responses.POST,
            "https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
            json=refresh_tokens,
            status=200,
            match=[
                urlencoded_params_matcher(
                    {
                        "client_id": "sdk",
                        "grant_type": "refresh_token",
                        "refresh_token": "kaboom",
                    }
                )
            ],
        )

        mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
        mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
        auth = Authenticator(
            ClientConfig(
                url="https://simai.ansys.com",
                organization="13_monkeys",
                credentials=Credentials(username="timmy", password="key"),
            ),
            niquests.Session(),
        )

        request = niquests.Request("GET", "https://simai.ansys.com/v2/models", auth=auth).prepare()
        assert request.headers.get("Authorization") == "Bearer check 1 2"
        assert request.headers.get("X-Org") == "13_monkeys"


@responses.activate
def test_authenticator_automatically_refreshes_auth_before_refresh_token_expires(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)

    auth_tokens = copy.deepcopy(DEFAULT_TOKENS)
    auth_tokens["access_token"] = "monkey-see"
    auth_tokens["expires_in"] = _AuthTokens.EXPIRATION_BUFFER - 1
    auth_tokens["refresh_expires_in"] = _AuthTokensRetriever.REFRESH_BUFFER + 1
    resps_direct_grant = responses.add(
        responses.POST,
        "https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=auth_tokens,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "client_id": "sdk",
                    "grant_type": "password",
                    "scope": "openid",
                    "username": "timmy",
                    "password": "key",
                }
            )
        ],
    )
    # Token refresh request
    refreshed_tokens = DEFAULT_TOKENS.copy()
    refreshed_tokens["access_token"] = "TFou"
    resps_refresh = responses.add(
        responses.POST,
        "https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
        json=refreshed_tokens,
        status=200,
        match=[
            urlencoded_params_matcher(
                {
                    "client_id": "sdk",
                    "grant_type": "refresh_token",
                    "refresh_token": "kaboom",
                }
            )
        ],
    )
    Authenticator(
        ClientConfig(
            url="https://simai.ansys.com",
            organization="14_monkeys",
            credentials=Credentials(username="timmy", password="key"),
        ),
        niquests.Session(),
    )
    assert resps_direct_grant.call_count == 1
    assert resps_refresh.call_count == 0
    t0 = time.time()
    while time.time() - t0 < 2 and resps_refresh.call_count == 0:
        # wait for the daemon thread to do its thing, or for the 2sec timeout...
        time.sleep(0.1)
    # Tokens are automatically refreshed so refresh token doesn't expire'
    assert resps_direct_grant.call_count == 1
    assert resps_refresh.call_count == 1


@responses.activate
def test_requests_outside_user_api_are_not_authentified(mocker, tmpdir):
    mocker.patch("ansys.simai.core.utils.auth.get_cache_dir", return_value=tmpdir)
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        # Authentication request
        keycloak_response_json = DEFAULT_TOKENS.copy()
        rsps.add(
            responses.POST,
            "https://simai.ansys.com/auth/realms/simai/protocol/openid-connect/token",
            json=keycloak_response_json,
            status=200,
        )

        auth = Authenticator(
            ClientConfig(
                url="https://simai.ansys.com",
                organization="Justice",
                credentials={"username": "timmy", "password": "D.A.N.C.E"},
            ),
            niquests.Session(),
        )
        request = niquests.Request("GET", "https://amazonaws.com/bloc-party", auth=auth).prepare()
        assert request.headers.get("Authorization") is None
        assert request.headers.get("X-Org") is None
