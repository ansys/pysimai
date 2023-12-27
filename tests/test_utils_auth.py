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

import json
import time

import pytest
import requests
import responses
from ansys.simai.core.errors import SimAIError
from ansys.simai.core.utils.auth import (
    Authenticator,
    _AuthTokens,
    _get_cached_or_request_device_auth,
)
from ansys.simai.core.utils.configuration import ClientConfig, Credentials
from responses.matchers import urlencoded_params_matcher

DEFAULT_TOKENS = {
    "access_token": "check",
    "expires_in": 6,
    "refresh_expires_in": 1800,
    "refresh_token": "kaboom",
}


@responses.activate
def test_request_auth_tokens_direct_grant():
    default_params = {"client_id": "sdk", "grant_type": "password", "scope": "openid"}
    responses.add(
        responses.POST,
        "http://myauthserver.com/",
        json={
            "error": "invalid_grant",
            "error_description": "Invalid user credentials",
        },
        status=401,
        match=[
            urlencoded_params_matcher(
                dict({"username": "macron", "password": "explosion"}, **default_params)
            )
        ],
    )

    with pytest.raises(SimAIError):
        _AuthTokens.from_request_direct_grant(
            session=requests.Session(),
            token_url="http://myauthserver.com/",
            creds=Credentials(username="macron", password="explosion"),
        )

    responses.add(
        responses.POST,
        "http://myauthserver.com/",
        json=DEFAULT_TOKENS,
        status=200,
        match=[urlencoded_params_matcher(dict({"username": "timmy"}, **default_params))],
    )

    tokens = _AuthTokens.from_request_direct_grant(
        session=requests.Session(),
        token_url="http://myauthserver.com/",
        creds=Credentials(username="timmy", password=""),
    )
    tokens_dict = tokens.dict()
    tokens_dict.pop("cache_file")
    tokens_dict.pop("expiration")
    tokens_dict.pop("refresh_expiration")
    assert tokens_dict == DEFAULT_TOKENS


@responses.activate
def test_request_auth_tokens_device_grant_with_bad_cache(mocker, tmpdir):
    """WHEN A device auth flow is requested
    AND a (bad) refresh token is cached
    THEN SDK tries to use the cached refresh token
    AND requests a device auth flow if the token is invalid
    """
    webbrowser_open = mocker.patch("webbrowser.open")
    mocker.patch("ansys.simai.core.utils.files.get_cache_dir", return_value=tmpdir)
    refresh_token = "spaghetti"
    device_code = "foxtrot uniform charlie kilo"
    token_url = "http://myauthserver.com/get-token"
    device_auth_url = "http://myauthserver.com/device-auth"

    fake_cache = _AuthTokens(
        access_token="",
        expires_in="0",
        refresh_expires_in="999",
        refresh_token=refresh_token,
    )
    with open(tmpdir / "tokens-lol.json", "w") as f:
        json.dump(fake_cache.json(), f)

    responses.add(  # error when app tries to use invalidated cached token
        responses.POST,
        token_url,
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
        device_auth_url,
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
        token_url,
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
    tokens = _get_cached_or_request_device_auth(
        session=requests.Session(),
        device_auth_url=device_auth_url,
        token_url=token_url,
        auth_cache_hash="lol",
    )
    webbrowser_open.assert_called_with("nope?code=abcdefg")
    tokens_dict = tokens.dict()
    tokens_dict.pop("cache_file")
    tokens_dict.pop("expiration")
    tokens_dict.pop("refresh_expiration")
    assert tokens_dict == DEFAULT_TOKENS


@responses.activate
def test_refresh_auth_tokens():
    tokens_dict = DEFAULT_TOKENS.copy()
    tokens_dict["refresh_token"] = "kabam"
    final_tokens = _AuthTokens(**tokens_dict, cache_file=None)

    responses.add(
        responses.POST,
        "http://myauthserver.com/",
        json={
            "error": "invalid_grant",
            "error_description": "Invalid user credentials",
        },
        status=401,
        match=[
            urlencoded_params_matcher(
                {
                    "client_id": "sdk",
                    "grant_type": "refresh_token",
                    "refresh_token": "gabuzomeu",
                }
            )
        ],
    )

    with pytest.raises(SimAIError):
        final_tokens.refresh(requests.Session(), "http://myauthserver.com/")

    tokens_dict["access_token"] = "new_tok"

    responses.add(
        responses.POST,
        "http://myauthserver.com/",
        json=tokens_dict,
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

    final_tokens = final_tokens.refresh(requests.Session(), "http://myauthserver.com/").dict()
    # Remove extra vars we don't want to check from the result
    final_tokens.pop("cache_file")
    final_tokens.pop("expiration")
    final_tokens.pop("refresh_expiration")
    assert final_tokens == tokens_dict


@responses.activate
def test_authenticator_automatically_refreshes_auth_before_requests_if_needed():
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        # Authentication request
        auth_tokens = DEFAULT_TOKENS.copy()
        auth_tokens["expires_in"] = 6
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
        refresh_tokens = DEFAULT_TOKENS.copy()
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

        auth = Authenticator(
            ClientConfig(
                url="https://simai.ansys.com",
                organization="13_monkeys",
                credentials=Credentials(username="timmy", password="key"),
                disable_cache=True,
            ),
            requests.Session(),
        )
        request = requests.Request("GET", "https://simai.ansys.com/v2/models", auth=auth).prepare()
        assert request.headers.get("Authorization") == "Bearer check"
        assert request.headers.get("X-Org") == "13_monkeys"

        time.sleep(2)

        request = requests.Request("GET", "https://simai.ansys.com/v2/models", auth=auth).prepare()

        assert request.headers.get("Authorization") == "Bearer check 1 2"
        assert request.headers.get("X-Org") == "13_monkeys"


@responses.activate
def test_authenticator_automatically_refreshes_auth_before_refresh_token_expires():
    with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
        # Authentication request
        auth_tokens = DEFAULT_TOKENS.copy()
        auth_tokens["access_token"] = "monkey-see"
        auth_tokens["expires_in"] = 1
        auth_tokens["refresh_expires_in"] = 31
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
        refreshed_tokens = DEFAULT_TOKENS.copy()
        refreshed_tokens["access_token"] = "TFou"
        rsps.add(
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

        auth = Authenticator(
            ClientConfig(
                url="https://simai.ansys.com",
                organization="14_monkeys",
                credentials=Credentials(username="timmy", password="key"),
                disable_cache=True,
            ),
            requests.Session(),
        )
        request = requests.Request("GET", "https://simai.ansys.com/v2/models", auth=auth).prepare()
        assert request.headers.get("Authorization") == "Bearer TFou"
        assert request.headers.get("X-Org") == "14_monkeys"

        time.sleep(2)
        # Refresh should have been called automatically by now, if it didn't test will fail


@responses.activate
def test_requests_outside_user_api_are_not_authentified():
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
                disable_cache=True,
            ),
            requests.Session(),
        )
        request = requests.Request("GET", "https://amazonaws.com/bloc-party", auth=auth).prepare()
        assert request.headers.get("Authorization") is None
        assert request.headers.get("X-Org") is None
